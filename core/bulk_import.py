"""Bulk import quiz questions from Excel, with optional image ZIP (together or separate)."""
from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

import config
from core import storage

# Columns accepted in the import template (case-insensitive aliases mapped to these)
_TEMPLATE_COLUMNS = [
    "question", "qtype", "opt_a", "opt_b", "opt_c", "opt_d",
    "correct", "timer_sec", "points", "image_file",
]
_COLUMN_ALIASES = {
    "q": "question", "prompt": "question", "text": "question",
    "type": "qtype", "question_type": "qtype",
    "option_a": "opt_a", "a": "opt_a",
    "option_b": "opt_b", "b": "opt_b",
    "option_c": "opt_c", "c": "opt_c",
    "option_d": "opt_d", "d": "opt_d",
    "answer": "correct", "correct_answer": "correct",
    "timer": "timer_sec", "time": "timer_sec",
    "image": "image_file", "img": "image_file", "media_file": "image_file",
    "filename": "image_file", "photo": "image_file",
}


@dataclass
class ImportResult:
    added: int = 0
    skipped: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.added > 0 and not self.errors


def template_bytes() -> bytes:
    """Downloadable Excel template with instructions + sample rows."""
    samples = pd.DataFrame([
        {
            "question": "What does FCR stand for in contact-centre KPIs?",
            "qtype": "mcq",
            "opt_a": "First Call Resolution",
            "opt_b": "Full Customer Refund",
            "opt_c": "Fast Cash Reversal",
            "opt_d": "Fraud Case Review",
            "correct": "A",
            "timer_sec": 20,
            "points": 1000,
            "image_file": "",
        },
        {
            "question": "Describe what you see in the compliance slide.",
            "qtype": "subjective",
            "opt_a": "", "opt_b": "", "opt_c": "", "opt_d": "",
            "correct": "",
            "timer_sec": 45,
            "points": 300,
            "image_file": "slide_kyc.png",
        },
    ])
    guide = pd.DataFrame([
        {"Topic": "Required", "Detail": "question — the prompt shown to players"},
        {"Topic": "Optional", "Detail": "qtype — mcq (default) or subjective"},
        {"Topic": "MCQ", "Detail": "opt_a … opt_d + correct letter A/B/C/D"},
        {"Topic": "Timing", "Detail": "timer_sec (default 20 MCQ / 45 subjective), points (default 1000)"},
        {"Topic": "Images", "Detail": "image_file — filename matching a file in your images ZIP (e.g. slide_kyc.png)"},
        {"Topic": "Separate upload", "Detail": "Upload this Excel first, then a ZIP of images in the second step"},
        {"Topic": "Combined ZIP", "Detail": "Pack questions.xlsx + image files (any folder) into one .zip"},
    ])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        samples.to_excel(writer, sheet_name="questions", index=False)
        guide.to_excel(writer, sheet_name="how_to", index=False)
    return buf.getvalue()


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for col in df.columns:
        key = str(col).strip().lower().replace(" ", "_")
        rename[col] = _COLUMN_ALIASES.get(key, key)
    return df.rename(columns=rename)


def _cell_str(val) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()


def parse_questions_excel(data: bytes, sheet: str | int = 0) -> tuple[list[dict], list[str]]:
    """Parse question rows from an Excel workbook."""
    errors: list[str] = []
    try:
        df = pd.read_excel(io.BytesIO(data), sheet_name=sheet, engine="openpyxl")
    except Exception as e:
        return [], [f"Could not read Excel file: {e}"]
    if df.empty:
        return [], ["The spreadsheet has no rows."]
    df = _normalize_columns(df)
    if "question" not in df.columns:
        return [], ["Missing a 'question' column — download the template and match its headers."]

    rows: list[dict] = []
    for i, r in df.iterrows():
        row_num = int(i) + 2  # header + 1-based
        question = _cell_str(r.get("question"))
        if not question:
            continue
        qtype = _cell_str(r.get("qtype", "mcq")).lower() or "mcq"
        if qtype not in ("mcq", "subjective"):
            errors.append(f"Row {row_num}: qtype must be mcq or subjective (got '{qtype}').")
            continue
        opts = [_cell_str(r.get(f"opt_{L.lower()}")) for L in "ABCD"]
        correct = _cell_str(r.get("correct", "A")).upper()[:1] or "A"
        if qtype == "mcq":
            if not all(opts):
                errors.append(f"Row {row_num}: MCQ needs all four options (opt_a … opt_d).")
                continue
            if correct not in "ABCD":
                errors.append(f"Row {row_num}: correct must be A, B, C, or D.")
                continue
        timer_raw = r.get("timer_sec")
        points_raw = r.get("points")
        try:
            timer = int(timer_raw) if _cell_str(timer_raw) else (
                config.SUBJECTIVE_TIMER_SEC if qtype == "subjective" else config.DEFAULT_TIMER_SEC)
        except (TypeError, ValueError):
            timer = config.SUBJECTIVE_TIMER_SEC if qtype == "subjective" else config.DEFAULT_TIMER_SEC
        try:
            points = int(points_raw) if _cell_str(points_raw) else config.BASE_POINTS
        except (TypeError, ValueError):
            points = config.BASE_POINTS
        rows.append({
            "row_num": row_num,
            "question": question,
            "qtype": qtype,
            "options": opts,
            "correct": correct if qtype == "mcq" else "",
            "timer_sec": max(10, min(120, timer)),
            "points": max(100, min(5000, points)),
            "image_file": _cell_str(r.get("image_file")),
        })
    if not rows and not errors:
        errors.append("No valid question rows found — fill the 'question' column.")
    return rows, errors


def extract_images_from_zip(data: bytes) -> tuple[dict[str, bytes], list[str]]:
    """Map lowercase basename -> file bytes for every image in a ZIP."""
    images: dict[str, bytes] = {}
    warnings: list[str] = []
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if name.endswith("/") or "__MACOSX" in name or name.startswith("."):
                    continue
                path = Path(name.replace("\\", "/"))
                ext = path.suffix.lower()
                if ext not in config.MEDIA_IMAGE_EXT:
                    continue
                if len(zf.read(name)) > config.MEDIA_MAX_BYTES:
                    warnings.append(f"Skipped {path.name} — over size limit.")
                    continue
                key = path.name.lower()
                images[key] = zf.read(name)
    except zipfile.BadZipFile:
        return {}, ["Invalid ZIP file — upload a .zip containing image files."]
    if not images:
        warnings.append("ZIP contained no image files (PNG, JPG, GIF, WebP).")
    return images, warnings


def parse_combined_zip(data: bytes) -> tuple[bytes | None, dict[str, bytes], list[str]]:
    """One ZIP with an Excel workbook + image files (any folder structure)."""
    errors: list[str] = []
    xlsx_data: bytes | None = None
    images: dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if name.endswith("/") or "__MACOSX" in name or name.startswith("."):
                    continue
                path = Path(name.replace("\\", "/"))
                ext = path.suffix.lower()
                if ext in (".xlsx", ".xls") and xlsx_data is None:
                    xlsx_data = zf.read(name)
                elif ext in config.MEDIA_IMAGE_EXT:
                    raw = zf.read(name)
                    if len(raw) <= config.MEDIA_MAX_BYTES:
                        images[path.name.lower()] = raw
    except zipfile.BadZipFile:
        return None, {}, ["Invalid ZIP — expected questions.xlsx plus image files inside."]
    if xlsx_data is None:
        errors.append("No .xlsx workbook found inside the ZIP.")
    return xlsx_data, images, errors


def _resolve_image(row: dict, images: dict[str, bytes], quiz_id: str,
                   row_idx: int) -> tuple[str, str, list[str]]:
    """Return media_type, media_file, warnings for one row."""
    warnings: list[str] = []
    spec = row.get("image_file", "").strip()
    data: bytes | None = None
    fname = ""
    if spec:
        key = Path(spec).name.lower()
        data = images.get(key)
        fname = Path(spec).name
    elif images:
        for pattern in (f"{row_idx}.png", f"{row_idx}.jpg", f"{row_idx}.jpeg",
                          f"q{row_idx}.png", f"q{row_idx}.jpg"):
            if pattern in images:
                data = images[pattern]
                fname = pattern
                break
    if not data:
        if spec:
            warnings.append(f'Row {row["row_num"]}: image "{spec}" not found in uploaded images.')
        return "", "", warnings
    try:
        mt, rel = storage.save_question_media(quiz_id, fname, data)
        return mt, rel, warnings
    except ValueError as e:
        warnings.append(f'Row {row["row_num"]}: {e}')
        return "", "", warnings


def import_questions(quiz_id: str, rows: list[dict], images: dict[str, bytes]) -> ImportResult:
    """Append parsed rows to a quiz, attaching images when available."""
    result = ImportResult()
    for idx, row in enumerate(rows, start=1):
        media_type, media_file, warns = _resolve_image(row, images, quiz_id, idx)
        result.warnings.extend(warns)
        try:
            storage.add_question(
                quiz_id,
                row["question"],
                row["options"],
                row["correct"],
                row["timer_sec"],
                row["points"],
                qtype=row["qtype"],
                media_type=media_type,
                media_file=media_file,
            )
            result.added += 1
        except Exception as e:
            result.errors.append(f'Row {row["row_num"]}: could not save — {e}')
            result.skipped += 1
    return result


def attach_images_to_quiz(quiz_id: str, mapping_rows: list[dict],
                          images: dict[str, bytes]) -> ImportResult:
    """Attach images to existing questions by q_index (1-based, matches Excel order in quiz)."""
    result = ImportResult()
    qs = storage.read_sheet(config.QUIZZES_XLSX, "questions")
    sub = qs[qs["quiz_id"].astype(str) == str(quiz_id)].sort_values("q_index")
    if sub.empty:
        result.errors.append("This quiz has no questions yet — import text first.")
        return result
    by_index = {int(r["q_index"]) + 1: i for i, r in sub.iterrows()}

    for row in mapping_rows:
        q_num = row.get("q_index")
        image_file = row.get("image_file", "").strip()
        if not image_file:
            continue
        if q_num is None or str(q_num).strip() == "":
            result.warnings.append(f'Skip row {row.get("row_num")}: missing q_index.')
            continue
        try:
            q_index_one = int(float(q_num))
        except (TypeError, ValueError):
            result.warnings.append(f'Invalid q_index "{q_num}".')
            continue
        df_idx = by_index.get(q_index_one)
        if df_idx is None:
            result.warnings.append(f'Question #{q_index_one} not found in quiz.')
            continue
        key = Path(image_file).name.lower()
        data = images.get(key)
        if not data:
            result.warnings.append(f'Image "{image_file}" not found in ZIP for Q{q_index_one}.')
            continue
        try:
            mt, rel = storage.save_question_media(quiz_id, Path(image_file).name, data)
            qs.at[df_idx, "media_type"] = mt
            qs.at[df_idx, "media_file"] = rel
            result.added += 1
        except ValueError as e:
            result.warnings.append(f'Q{q_index_one}: {e}')

    if result.added:
        storage.write_sheet(config.QUIZZES_XLSX, "questions", qs)
    return result


def parse_image_mapping_excel(data: bytes) -> tuple[list[dict], list[str]]:
    """Parse q_index + image_file rows for attaching images separately."""
    try:
        df = pd.read_excel(io.BytesIO(data), sheet_name=0, engine="openpyxl")
    except Exception as e:
        return [], [f"Could not read mapping Excel: {e}"]
    df = _normalize_columns(df)
    if "image_file" not in df.columns:
        return [], ["Mapping sheet needs an 'image_file' column."]
    rows = []
    for i, r in df.iterrows():
        img = _cell_str(r.get("image_file"))
        if not img:
            continue
        q_idx = r.get("q_index", r.get("question", i + 1))
        rows.append({"row_num": int(i) + 2, "q_index": q_idx, "image_file": img})
    return rows, []


def create_import_quiz(title: str, emoji: str, created_by: str) -> str:
    quiz_id = "import-" + datetime.now().strftime("%y%m%d-%H%M%S")
    storage.add_quiz(quiz_id, title.strip(), emoji, "Imported", config.DEFAULT_TIMER_SEC, created_by)
    return quiz_id
