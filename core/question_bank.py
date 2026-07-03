"""Banking-domain question bank — generates data/question_bank.xlsx (2,000 questions).

Categories: Banking Operations · KPI & Metrics · Customer Service ·
            Self-Service & Digital · IVR · Agent Assist & LLM · Subjective (voting rounds)

Everything is generated locally and deterministically (seeded) — no internet needed.
The Excel file is the single source of truth; admins build quizzes from it in the app.
"""
import random
from datetime import datetime

import pandas as pd

import config
from core import storage

CAT_OPS = "Banking Operations"
CAT_KPI = "KPI & Metrics"
CAT_CS = "Customer Service"
CAT_SS = "Self-Service & Digital"
CAT_IVR = "IVR"
CAT_AI = "Agent Assist & LLM"
CAT_SUBJ = "Subjective (Vote Round)"

CATEGORIES = [CAT_OPS, CAT_KPI, CAT_CS, CAT_SS, CAT_IVR, CAT_AI, CAT_SUBJ]

BANK_COLS = ["qid", "category", "difficulty", "qtype", "question",
             "opt_a", "opt_b", "opt_c", "opt_d", "correct", "timer_sec", "points"]

# ============================================================
# Term glossary: (abbr, expansion, plain-english definition, category)
# ============================================================
TERMS = [
    # ---- KPI & Metrics ----
    ("AHT", "Average Handle Time", "average talk + hold + after-call work time per handled contact", CAT_KPI),
    ("ASA", "Average Speed of Answer", "average time a caller waits before an agent answers", CAT_KPI),
    ("ACW", "After Call Work", "time an agent spends on wrap-up tasks after the interaction ends", CAT_KPI),
    ("ATT", "Average Talk Time", "average duration agents spend talking per call", CAT_KPI),
    ("FCR", "First Contact Resolution", "share of issues fully resolved in the very first contact", CAT_KPI),
    ("CSAT", "Customer Satisfaction Score", "survey score of how satisfied customers are with the service", CAT_KPI),
    ("NPS", "Net Promoter Score", "percentage of promoters minus percentage of detractors on the 0-10 recommend scale", CAT_KPI),
    ("CES", "Customer Effort Score", "how easy customers found it to get their issue resolved", CAT_KPI),
    ("SLA", "Service Level Agreement", "committed service target, e.g. answering 80% of calls within 20 seconds", CAT_KPI),
    ("ABN", "Abandonment Rate", "share of callers who hang up before reaching an agent", CAT_KPI),
    ("OCC", "Occupancy Rate", "share of logged-in time agents spend handling contacts versus waiting idle", CAT_KPI),
    ("ADH", "Schedule Adherence", "how closely agents follow their planned schedule", CAT_KPI),
    ("SHR", "Shrinkage", "paid time agents are unavailable to handle contacts (leave, training, breaks)", CAT_KPI),
    ("MTTR", "Mean Time To Resolution", "average time taken to fully resolve an issue", CAT_KPI),
    ("CPC", "Cost Per Contact", "total operating cost divided by number of contacts handled", CAT_KPI),
    ("CPH", "Contacts Per Hour", "contacts an agent handles per productive hour", CAT_KPI),
    ("QA", "Quality Assurance Score", "evaluation score of an interaction against the quality scorecard", CAT_KPI),
    ("DSAT", "Customer Dissatisfaction Score", "share of customers rating the service negatively", CAT_KPI),
    ("AWT", "Average Wait Time", "mean queue time experienced by customers before being served", CAT_KPI),
    ("FRT", "First Response Time", "time until the customer receives the first human response", CAT_KPI),
    ("RR", "Repeat Contact Rate", "share of customers contacting again about the same issue", CAT_KPI),
    ("UTIL", "Utilisation", "share of paid time an agent spends on contact-handling work", CAT_KPI),
    ("TAT", "Turnaround Time", "time taken to complete a request end to end", CAT_KPI),
    ("XFR", "Transfer Rate", "share of calls transferred to another agent or queue", CAT_KPI),
    ("SL", "Service Level", "percentage of calls answered within the target threshold time", CAT_KPI),
    ("BKLG", "Backlog", "volume of pending unresolved cases in the queue", CAT_KPI),
    ("ATTR", "Attrition Rate", "rate at which agents leave the team over a period", CAT_KPI),
    ("RESR", "Resolution Rate", "share of contacts fully resolved regardless of number of contacts", CAT_KPI),

    # ---- Banking Operations ----
    ("KYC", "Know Your Customer", "verifying a customer's identity before and during the relationship", CAT_OPS),
    ("AML", "Anti-Money Laundering", "controls that prevent disguising illegally obtained funds", CAT_OPS),
    ("CDD", "Customer Due Diligence", "risk assessment of a customer performed at onboarding", CAT_OPS),
    ("EDD", "Enhanced Due Diligence", "deeper background checks applied to high-risk customers", CAT_OPS),
    ("PEP", "Politically Exposed Person", "customer holding a prominent public function who needs extra scrutiny", CAT_OPS),
    ("STR", "Suspicious Transaction Report", "report filed with the regulator on suspicious account activity", CAT_OPS),
    ("CTR", "Currency Transaction Report", "regulatory report filed for large cash transactions", CAT_OPS),
    ("RTGS", "Real Time Gross Settlement", "instant one-by-one settlement of high-value fund transfers", CAT_OPS),
    ("NEFT", "National Electronic Funds Transfer", "batch-settled electronic fund transfer system in India", CAT_OPS),
    ("IMPS", "Immediate Payment Service", "24x7 instant interbank transfer service", CAT_OPS),
    ("UPI", "Unified Payments Interface", "instant mobile payment system using virtual payment addresses", CAT_OPS),
    ("NACH", "National Automated Clearing House", "bulk mandate-based debit and credit processing", CAT_OPS),
    ("CTS", "Cheque Truncation System", "clearing cheques using images instead of moving paper", CAT_OPS),
    ("MICR", "Magnetic Ink Character Recognition", "machine-readable code line printed on cheques", CAT_OPS),
    ("IFSC", "Indian Financial System Code", "code identifying a specific bank branch for transfers", CAT_OPS),
    ("SWIFT", "Society for Worldwide Interbank Financial Telecommunication", "global network for international payment messaging", CAT_OPS),
    ("IBAN", "International Bank Account Number", "standardised international account identifier", CAT_OPS),
    ("ACH", "Automated Clearing House", "batch electronic network for low-value payments", CAT_OPS),
    ("POS", "Point of Sale", "terminal or location where card payments are accepted", CAT_OPS),
    ("EMV", "Europay Mastercard Visa", "global chip-card security standard", CAT_OPS),
    ("CVV", "Card Verification Value", "three-digit security code printed on payment cards", CAT_OPS),
    ("OTP", "One Time Password", "single-use code used to authenticate a transaction or login", CAT_OPS),
    ("2FA", "Two Factor Authentication", "verifying identity using two independent factors", CAT_OPS),
    ("NPA", "Non Performing Asset", "loan on which repayments are overdue beyond 90 days", CAT_OPS),
    ("CASA", "Current Account Savings Account", "low-cost deposit base made of current and savings accounts", CAT_OPS),
    ("GL", "General Ledger", "master record of all the bank's accounting entries", CAT_OPS),
    ("RCA", "Root Cause Analysis", "structured search for the underlying cause of a defect", CAT_OPS),
    ("SOP", "Standard Operating Procedure", "documented step-by-step instructions for a process", CAT_OPS),
    ("EOD", "End of Day", "closing batch processing run after business hours", CAT_OPS),
    ("FATCA", "Foreign Account Tax Compliance Act", "US law requiring reporting of foreign-held accounts", CAT_OPS),
    ("LEI", "Legal Entity Identifier", "global identifier for legal parties in financial transactions", CAT_OPS),
    ("DD", "Demand Draft", "prepaid negotiable instrument issued by a bank", CAT_OPS),
    ("CBK", "Chargeback", "card transaction reversed after a customer dispute", CAT_OPS),
    ("RECON", "Reconciliation", "matching internal records against external statements to find breaks", CAT_OPS),
    ("MKR-CHKR", "Maker-Checker", "control where one person enters and a second person approves", CAT_OPS),

    # ---- Customer Service ----
    ("CRM", "Customer Relationship Management", "system holding customer history and every interaction", CAT_CS),
    ("VOC", "Voice of the Customer", "programme that captures and analyses customer feedback", CAT_CS),
    ("CX", "Customer Experience", "end-to-end perception a customer has of the bank", CAT_CS),
    ("CTI", "Computer Telephony Integration", "linking the phone system with desktop apps for screen pops", CAT_CS),
    ("WFM", "Workforce Management", "forecasting volumes and scheduling agent staffing", CAT_CS),
    ("WFO", "Workforce Optimisation", "combined suite of QA, coaching and scheduling", CAT_CS),
    ("CSR", "Customer Service Representative", "front-line agent serving customers", CAT_CS),
    ("ESC", "Escalation", "routing an issue to higher expertise or authority", CAT_CS),
    ("FLR", "First Line Resolution", "resolving at the first support tier without escalation", CAT_CS),
    ("HOLD", "Hold Time", "time a customer spends on hold during a call", CAT_CS),
    ("CBAK", "Callback", "phoning the customer back so they don't wait in queue", CAT_CS),
    ("SRQ", "Service Request", "logged request for a service action on an account", CAT_CS),
    ("TKT", "Ticket", "tracked record of a customer issue through to closure", CAT_CS),
    ("CHURN", "Churn Rate", "share of customers who leave over a period", CAT_CS),
    ("RET", "Retention Rate", "share of customers successfully kept over a period", CAT_CS),
    ("EMP", "Empathy Statement", "phrase that acknowledges the customer's feelings before solving", CAT_CS),
    ("VERB", "Survey Verbatim", "free-text comment a customer writes in a survey", CAT_CS),
    ("CLF", "Closed Loop Feedback", "calling back customers who gave poor scores to fix and learn", CAT_CS),
    ("SOFT", "Soft Skills", "communication behaviours like tone, pace and empathy", CAT_CS),
    ("PKB", "Positive Key Behaviour", "scripted behaviour proven to lift customer satisfaction", CAT_CS),

    # ---- Self-Service & Digital ----
    ("KBA", "Knowledge Base Article", "help article customers read to solve issues themselves", CAT_SS),
    ("FAQ", "Frequently Asked Questions", "curated list of common questions with answers", CAT_SS),
    ("CONT", "Containment Rate", "share of sessions fully handled by self-service without an agent", CAT_SS),
    ("DEFL", "Deflection Rate", "contacts avoided because self-service answered them first", CAT_SS),
    ("SSR", "Self Service Rate", "share of transactions completed without human help", CAT_SS),
    ("DADOPT", "Digital Adoption", "share of customers actively using digital channels", CAT_SS),
    ("MBANK", "Mobile Banking", "banking done through the bank's mobile app", CAT_SS),
    ("NBANK", "Net Banking", "banking done through the web portal", CAT_SS),
    ("PWDR", "Password Reset Flow", "automated journey for recovering login credentials", CAT_SS),
    ("CHBOT", "Chatbot", "automated conversational assistant on chat channels", CAT_SS),
    ("COBRW", "Co-browsing", "agent securely viewing and guiding the customer's screen", CAT_SS),
    ("EKYC", "Electronic KYC", "paperless digital identity verification", CAT_SS),
    ("DIY", "Do-It-Yourself Journey", "guided flow a customer completes entirely alone", CAT_SS),
    ("OMNI", "Omnichannel", "seamless experience across channels with shared context", CAT_SS),
    ("DROP", "Journey Drop-off", "point where customers abandon a digital flow", CAT_SS),

    # ---- IVR ----
    ("IVR", "Interactive Voice Response", "automated phone menu that speaks to and listens to callers", CAT_IVR),
    ("DTMF", "Dual Tone Multi Frequency", "touch-tone keypad input during calls", CAT_IVR),
    ("ASR", "Automatic Speech Recognition", "converting caller speech into text", CAT_IVR),
    ("TTS", "Text To Speech", "converting text into spoken audio prompts", CAT_IVR),
    ("NLUI", "Natural Language Understanding (IVR)", "extracting caller intent from free speech instead of menus", CAT_IVR),
    ("ACD", "Automatic Call Distributor", "system that routes incoming calls to queues and agents", CAT_IVR),
    ("SBR", "Skill Based Routing", "sending calls to agents who have the matching skill", CAT_IVR),
    ("ANI", "Automatic Number Identification", "caller's phone number captured automatically", CAT_IVR),
    ("DNIS", "Dialed Number Identification Service", "identifying which number the caller dialled", CAT_IVR),
    ("SPOP", "Screen Pop", "customer record opening automatically as the call arrives", CAT_IVR),
    ("BARGE", "Barge-In", "letting callers interrupt a prompt by speaking or pressing a key", CAT_IVR),
    ("OPTR", "Opt-Out Rate", "share of callers pressing to leave the IVR for an agent", CAT_IVR),
    ("MDEP", "Menu Depth", "number of menu layers a caller must navigate", CAT_IVR),
    ("CCB", "Courtesy Callback", "IVR offering to call back instead of making the caller hold", CAT_IVR),
    ("VUI", "Voice User Interface", "designing conversations for voice systems", CAT_IVR),

    # ---- Agent Assist & LLM ----
    ("LLM", "Large Language Model", "AI model trained on text to understand and generate language", CAT_AI),
    ("NLP", "Natural Language Processing", "field of AI focused on understanding human language", CAT_AI),
    ("NLG", "Natural Language Generation", "automatically producing human-like text", CAT_AI),
    ("RAG", "Retrieval Augmented Generation", "grounding LLM answers in documents retrieved at question time", CAT_AI),
    ("PRMPT", "Prompt Engineering", "crafting instructions to get better outputs from an LLM", CAT_AI),
    ("HALL", "Hallucination", "confident but factually wrong output from an LLM", CAT_AI),
    ("FTUNE", "Fine-Tuning", "further training a model on domain-specific data", CAT_AI),
    ("EMB", "Embeddings", "numeric vectors that represent the meaning of text", CAT_AI),
    ("VDB", "Vector Database", "store for embeddings that enables semantic search", CAT_AI),
    ("TOKN", "Token", "chunk of text a model reads or writes, roughly part of a word", CAT_AI),
    ("CTXW", "Context Window", "maximum amount of text a model can consider at once", CAT_AI),
    ("SENT", "Sentiment Analysis", "detecting emotion and polarity in text or speech", CAT_AI),
    ("INTD", "Intent Detection", "classifying what the customer actually wants", CAT_AI),
    ("AAST", "Agent Assist", "real-time AI suggestions shown to agents during interactions", CAT_AI),
    ("ASUM", "Auto-Summarisation", "AI writing the interaction summary automatically", CAT_AI),
    ("STT", "Speech To Text", "transcribing call audio into text in real time", CAT_AI),
    ("GRDR", "Guardrails", "controls that keep AI outputs safe and on-policy", CAT_AI),
    ("PIIR", "PII Redaction", "masking personal data inside transcripts and logs", CAT_AI),
    ("ZSHOT", "Zero-Shot Learning", "model performing a task with no examples given", CAT_AI),
    ("FSHOT", "Few-Shot Learning", "guiding a model with a handful of examples in the prompt", CAT_AI),
    ("TEMPR", "Temperature", "setting that controls the randomness of model output", CAT_AI),
    ("HITL", "Human In The Loop", "human review step placed over AI decisions", CAT_AI),
    ("DRIFT", "Model Drift", "model quality degrading as real-world data changes", CAT_AI),
    ("KMS", "Knowledge Management System", "curated content repository that powers assist tools", CAT_AI),
    ("NBA", "Next Best Action", "AI recommending the most useful next step for the customer", CAT_AI),
    ("AQA", "Auto QA", "AI scoring 100% of interactions against the quality scorecard", CAT_AI),
]

# ============================================================
# Curated scenario MCQs: (question, [4 options], correct_index, category, difficulty)
# ============================================================
SCENARIOS = [
    ("A customer calls angry after being transferred three times. What should the agent do FIRST?",
     ["Transfer to a supervisor immediately", "Acknowledge the frustration and own the issue",
      "Explain why the transfers happened", "Offer compensation straight away"], 1, CAT_CS, "easy"),
    ("Your FCR is falling while repeat calls rise. Which is the BEST first step?",
     ["Hire more agents", "Analyse repeat-call reasons to find the top failure driver",
      "Shorten AHT targets", "Add more IVR menu options"], 1, CAT_KPI, "medium"),
    ("A caller says 'I lost my debit card' to the open-ended IVR prompt. Which technology maps this to the card-block flow?",
     ["DTMF", "Natural Language Understanding", "Text To Speech", "Screen pop"], 1, CAT_IVR, "easy"),
    ("Occupancy has hit 96% for three weeks. What is the MOST likely outcome if nothing changes?",
     ["Higher CSAT", "Agent burnout and rising attrition", "Lower AHT", "Better adherence"], 1, CAT_KPI, "medium"),
    ("Which action MOST directly improves IVR containment?",
     ["Adding more agents", "Fixing the top failed self-service intents",
      "Longer welcome message", "Reducing agent breaks"], 1, CAT_IVR, "medium"),
    ("An LLM agent-assist tool suggests an answer that contradicts the policy document. What should the agent do?",
     ["Read it to the customer anyway", "Follow the policy document and flag the suggestion",
      "End the call", "Ask the customer what they prefer"], 1, CAT_AI, "easy"),
    ("A customer's UPI payment failed but money was debited. The standard reassurance is:",
     ["The money is lost and cannot be traced", "Failed UPI debits are typically auto-reversed within the TAT",
      "They must visit the branch immediately", "They should retry the payment 5 times"], 1, CAT_OPS, "easy"),
    ("Which metric pair often moves in OPPOSITE directions if you push agents too hard on speed?",
     ["AHT and ASA", "AHT and CSAT", "NPS and CSAT", "SL and ASA"], 1, CAT_KPI, "medium"),
    ("The chatbot resolves 60% of chats but customers who fail in the bot are angrier on arrival. The BEST fix is:",
     ["Remove the chatbot", "Seamless context handover so customers never repeat themselves",
      "Make the bot harder to exit", "Reduce agent headcount"], 1, CAT_SS, "medium"),
    ("For a suspected fraudulent transaction reported on a call, the FIRST action is:",
     ["Raise a service request for next week", "Block the card/channel immediately per SOP",
      "Ask the customer to email details", "Advise waiting for the statement"], 1, CAT_OPS, "easy"),
    ("Real-time agent assist adds the most value when it:",
     ["Replaces the agent entirely", "Surfaces the right knowledge at the right moment",
      "Emails the customer afterwards", "Slows the conversation down"], 1, CAT_AI, "easy"),
    ("Which is the classic 80/20 formulation of Service Level?",
     ["80% of calls resolved in 20 minutes", "80% of calls answered within 20 seconds",
      "80 agents per 20 queues", "80% CSAT with 20% DSAT"], 1, CAT_KPI, "easy"),
    ("A PEP wants to open a premium account. Operations must:",
     ["Decline automatically", "Apply Enhanced Due Diligence before onboarding",
      "Skip KYC for VIPs", "Open first, verify later"], 1, CAT_OPS, "medium"),
    ("Customers abandon the password-reset flow at the OTP step. Best diagnostic first move?",
     ["Rebuild the whole app", "Check OTP delivery latency and failure logs",
      "Remove the OTP step", "Add a captcha"], 1, CAT_SS, "medium"),
    ("Barge-in in an IVR means:",
     ["Agents interrupting customers", "Callers can respond before the prompt finishes",
      "Supervisors joining calls", "IVR hanging up on silence"], 1, CAT_IVR, "easy"),
    ("Auto-summarisation of calls primarily reduces which metric?",
     ["CSAT", "After Call Work", "Service Level", "NPS"], 1, CAT_AI, "easy"),
    ("Which control prevents one person from both entering and approving a payment?",
     ["Chargeback", "Maker-checker", "Reconciliation", "EOD batch"], 1, CAT_OPS, "easy"),
    ("NPS is calculated from responses to which question?",
     ["How satisfied were you today?", "How likely are you to recommend us (0-10)?",
      "Was your issue resolved?", "How easy was it to reach us?"], 1, CAT_KPI, "easy"),
    ("An agent sees the full customer journey the moment a call lands. This is enabled by:",
     ["ANI + CTI screen pop", "Longer IVR menus", "Higher occupancy", "Manual CRM search"], 0, CAT_IVR, "medium"),
    ("The safest way to use LLM output that cites account-specific facts is to:",
     ["Trust it if it sounds right", "Ground it with RAG and verify against the system of record",
      "Raise temperature for confidence", "Use a bigger model"], 1, CAT_AI, "medium"),
    ("Shrinkage includes all of these EXCEPT:",
     ["Training time", "Annual leave", "Coaching sessions", "Time spent talking to customers"], 3, CAT_KPI, "medium"),
    ("A customer wants to know why their cheque bounced. The polite, compliant first step is:",
     ["Quote the exact reason code from the system and explain simply", "Say it's the other bank's fault",
      "Ask them to visit any branch", "Tell them cheques are outdated"], 0, CAT_CS, "easy"),
    ("Which improvement typically raises digital adoption MOST?",
     ["TV advertising", "Removing friction from the first-time login journey",
      "Longer branch hours", "More IVR options"], 1, CAT_SS, "medium"),
    ("Intent detection on chat routes 'I want to close my account' to:",
     ["Card block flow", "Retention specialist queue", "Balance enquiry bot", "Locator page"], 1, CAT_AI, "easy"),
    ("Calls are answered fast but customers still rate effort as high. Which metric captures their pain?",
     ["ASA", "CES", "Occupancy", "Adherence"], 1, CAT_KPI, "medium"),
    ("Cheque images move through clearing instead of paper. This system is:",
     ["MICR", "CTS", "NACH", "RTGS"], 1, CAT_OPS, "easy"),
    ("Which is a healthy use of QA + Auto QA together?",
     ["Replace human QA entirely on day one", "Auto QA screens 100%, humans deep-dive flagged calls",
      "Score only the best agents", "Only audit short calls"], 1, CAT_AI, "medium"),
    ("The IVR asks the same authentication question the agent repeats later. Customers hate this. The fix is:",
     ["Remove authentication", "Pass IVR authentication context to the agent desktop",
      "Make agents faster", "Add a third verification"], 1, CAT_IVR, "medium"),
    ("Customer effort drops the MOST when:",
     ["The customer never has to contact you at all", "Hold music is nicer",
      "Surveys are shorter", "Agents talk faster"], 0, CAT_CS, "medium"),
    ("Which report is filed when a large CASH deposit crosses the regulatory threshold?",
     ["STR", "CTR", "KYC", "LEI"], 1, CAT_OPS, "medium"),
]

# Benefit-style questions: (topic, its real benefit, category)
BENEFITS = [
    ("courtesy callback", "customers keep their place in queue without holding", CAT_IVR),
    ("skill based routing", "customers reach the agent best equipped for their issue", CAT_IVR),
    ("screen pop via CTI", "agents greet customers with context, cutting handle time", CAT_IVR),
    ("natural language IVR", "callers say their need instead of memorising menus", CAT_IVR),
    ("agent assist", "agents get real-time answers without putting customers on hold", CAT_AI),
    ("auto-summarisation", "after-call work shrinks and notes become consistent", CAT_AI),
    ("RAG grounding", "AI answers cite current policy documents instead of guessing", CAT_AI),
    ("PII redaction", "personal data is masked before transcripts are stored", CAT_AI),
    ("sentiment analysis", "supervisors can spot struggling calls while they happen", CAT_AI),
    ("auto QA", "every interaction gets scored instead of a 2% sample", CAT_AI),
    ("chatbot containment", "routine queries resolve instantly at near-zero cost", CAT_SS),
    ("knowledge base articles", "customers self-solve at 2am without waiting for staff", CAT_SS),
    ("e-KYC", "onboarding completes in minutes without paper documents", CAT_SS),
    ("co-browsing", "agents guide confused customers through screens visually", CAT_SS),
    ("omnichannel context", "customers never repeat their story across channels", CAT_SS),
    ("first contact resolution focus", "repeat calls fall and customer effort drops", CAT_KPI),
    ("schedule adherence tracking", "queues stay covered exactly when volume arrives", CAT_KPI),
    ("closed loop feedback", "unhappy customers are called back and recovered", CAT_CS),
    ("empathy statements", "customers feel heard before the fix begins", CAT_CS),
    ("voice of the customer programme", "product fixes get driven by real feedback themes", CAT_CS),
    ("workforce management", "the right number of agents are staffed for forecast volume", CAT_CS),
    ("maker-checker control", "a second pair of eyes catches errors before they post", CAT_OPS),
    ("reconciliation", "breaks between systems are caught and fixed daily", CAT_OPS),
    ("standard operating procedures", "every agent handles the process the same correct way", CAT_OPS),
    ("root cause analysis", "the same incident stops recurring month after month", CAT_OPS),
    ("real time gross settlement", "high-value payments settle instantly and irrevocably", CAT_OPS),
]

FAKE_BENEFITS = [
    "agents can skip authentication for speed",
    "customers are automatically upsold on every call",
    "hold time is hidden from reports",
    "the metric dashboard turns green regardless of performance",
    "calls are ended automatically after 3 minutes",
    "customers are routed randomly to build agent variety",
    "survey scores below 4 are deleted",
    "agents no longer need product knowledge",
    "the queue plays double-speed music",
    "reports are only generated once a year",
]

# Subjective prompts for voting rounds
SUBJECTIVE_SCENARIOS = [
    "A customer has been double-charged and is furious. What EXACTLY would you say in your first two sentences?",
    "Describe one idea to cut repeat calls in your process by half.",
    "An elderly customer struggles with the mobile app. How would you help without pushing them away from digital?",
    "Pitch one creative use of an LLM to make agents' lives easier.",
    "What is the most broken part of a typical bank IVR, and how would you redesign it?",
    "A customer threatens to close all accounts over a ₹120 fee. How do you save the relationship?",
    "Invent a new KPI the team should track — name it and defend it.",
    "How would you explain 'why KYC matters' to an annoyed customer in one breath?",
    "Describe the perfect handover from chatbot to human agent.",
    "One process in operations wastes the most time. Which one, and what's your fix?",
    "Write the ideal empathy statement for a customer whose salary credit is delayed.",
    "How should a bank use AI WITHOUT losing the human touch? One concrete idea.",
    "Your queue is on fire: 40 calls waiting, 5 agents. What do you do in the next 10 minutes?",
    "What would make customers actually WANT to use self-service first?",
    "Describe your dream agent-assist screen — what's on it?",
    "A VIP customer got wrong information yesterday. Draft your callback opening line.",
    "Which single metric would you sacrifice to improve customer experience, and why?",
    "How would you detect a struggling new joiner from their metrics alone?",
    "Propose one 'wow moment' the team could deliver on every call at zero cost.",
    "What should the IVR say to a customer calling for the third time today?",
]


# ============================================================
# Generators
# ============================================================

def _letters(idx: int) -> str:
    return "ABCD"[idx]


def _mk(rng, question, options, correct_idx, category, difficulty, qtype="mcq",
        timer=None, points=None) -> dict:
    """Build one bank row, shuffling options."""
    if qtype == "mcq":
        order = list(range(4))
        rng.shuffle(order)
        opts = [options[i] for i in order]
        correct = _letters(order.index(correct_idx))
    else:
        opts = ["", "", "", ""]
        correct = ""
    return {
        "category": category, "difficulty": difficulty, "qtype": qtype, "question": question,
        "opt_a": opts[0], "opt_b": opts[1], "opt_c": opts[2], "opt_d": opts[3],
        "correct": correct,
        "timer_sec": timer or (config.SUBJECTIVE_TIMER_SEC if qtype == "subjective" else config.DEFAULT_TIMER_SEC),
        "points": points or config.BASE_POINTS,
    }


def _term_questions(rng) -> list[dict]:
    rows = []
    by_cat = {}
    for t in TERMS:
        by_cat.setdefault(t[3], []).append(t)

    for abbr, expansion, definition, cat in TERMS:
        pool = [t for t in by_cat[cat] if t[0] != abbr] or [t for t in TERMS if t[0] != abbr]

        # 1. acronym expansion
        if abbr.replace("-", "").replace("2", "").isupper() and abbr != expansion:
            distr = [t[1] for t in rng.sample(pool, 3)]
            rows.append(_mk(rng, f"What does {abbr} stand for?",
                            [expansion] + distr, 0, cat, "easy"))

        # 2. definition -> term
        distr = [f"{t[0]} ({t[1]})" for t in rng.sample(pool, 3)]
        rows.append(_mk(rng, f"Which term matches this definition: “{definition}”?",
                        [f"{abbr} ({expansion})"] + distr, 0, cat, "easy"))

        # 3. term -> definition
        distr = [t[2] for t in rng.sample(pool, 3)]
        rows.append(_mk(rng, f"{abbr} — {expansion} — is best described as…",
                        [definition] + distr, 0, cat, "medium"))

        # 4. true statement pick
        distr = [f"{abbr} means: {t[2]}" for t in rng.sample(pool, 3)]
        rows.append(_mk(rng, f"Which statement about {abbr} is TRUE?",
                        [f"{abbr} means: {definition}"] + distr, 0, cat, "medium"))
    return rows


def _pct_options(rng, correct: float) -> tuple[list[str], int]:
    """Correct % answer + 3 plausible distractors."""
    vals = {round(correct, 1)}
    while len(vals) < 4:
        delta = rng.choice([-12, -8, -5, -3, 3, 5, 8, 12, 15])
        v = round(correct + delta + rng.choice([0, 0.5]), 1)
        if 0 <= v <= 100:
            vals.add(v)
    opts = sorted(vals)
    return [f"{v:g}%" for v in opts], opts.index(round(correct, 1))


def _numeric_questions(rng, count: int) -> list[dict]:
    """KPI calculation questions with generated numbers."""
    rows = []
    makers = []

    def fcr():
        total = rng.randrange(200, 2000, 50); res = round(total * rng.uniform(0.55, 0.92))
        pct = 100 * res / total
        opts, ci = _pct_options(rng, pct)
        return (f"A team handled {total} contacts; {res} were resolved on first contact. What is the FCR?",
                opts, ci, CAT_KPI, "medium")
    makers.append(fcr)

    def abandon():
        offered = rng.randrange(300, 3000, 100); ab = round(offered * rng.uniform(0.02, 0.18))
        opts, ci = _pct_options(rng, 100 * ab / offered)
        return (f"{offered} calls were offered and {ab} callers hung up before answer. What is the abandonment rate?",
                opts, ci, CAT_KPI, "medium")
    makers.append(abandon)

    def slevel():
        offered = rng.randrange(400, 2400, 100); within = round(offered * rng.uniform(0.6, 0.95))
        opts, ci = _pct_options(rng, 100 * within / offered)
        return (f"Of {offered} answered calls, {within} were answered within the 20-second threshold. Service Level = ?",
                opts, ci, CAT_KPI, "medium")
    makers.append(slevel)

    def aht():
        calls = rng.randrange(20, 60, 5)
        talk = rng.randrange(60, 240) * calls; hold = rng.randrange(5, 40) * calls; acw = rng.randrange(15, 60) * calls
        correct = round((talk + hold + acw) / calls)
        vals = {correct}
        while len(vals) < 4:
            vals.add(correct + rng.choice([-60, -30, -15, 15, 30, 60, 90]))
        opts = sorted(v for v in vals if v > 0)[:4]
        while len(opts) < 4:
            opts.append(opts[-1] + 25)
        return (f"An agent handled {calls} calls with total talk {talk}s, hold {hold}s and ACW {acw}s. AHT in seconds = ?",
                [f"{v} sec" for v in opts], opts.index(correct), CAT_KPI, "hard")
    makers.append(aht)

    def occupancy():
        handle = rng.randrange(300, 420) ; idle = rng.randrange(20, 140)
        opts, ci = _pct_options(rng, 100 * handle / (handle + idle))
        return (f"An agent spent {handle} minutes handling contacts and {idle} minutes waiting. Occupancy = ?",
                opts, ci, CAT_KPI, "hard")
    makers.append(occupancy)

    def csat():
        resp = rng.randrange(80, 600, 20); sat = round(resp * rng.uniform(0.6, 0.95))
        opts, ci = _pct_options(rng, 100 * sat / resp)
        return (f"{resp} customers answered the survey; {sat} rated 4 or 5. CSAT = ?",
                opts, ci, CAT_KPI, "medium")
    makers.append(csat)

    def nps():
        p = rng.randrange(30, 70); d = rng.randrange(5, min(40, p))
        correct = p - d
        vals = {correct}
        while len(vals) < 4:
            vals.add(correct + rng.choice([-20, -10, -5, 5, 10, 20]))
        opts = sorted(vals)
        return (f"In an NPS survey, {p}% were promoters, {d}% detractors and the rest passives. NPS = ?",
                [str(v) for v in opts], opts.index(correct), CAT_KPI, "medium")
    makers.append(nps)

    def containment():
        sessions = rng.randrange(500, 5000, 100); cont = round(sessions * rng.uniform(0.35, 0.8))
        opts, ci = _pct_options(rng, 100 * cont / sessions)
        return (f"The IVR handled {sessions} calls; {cont} completed without reaching an agent. Containment rate = ?",
                opts, ci, CAT_IVR, "medium")
    makers.append(containment)

    def shrinkage():
        sched = rng.randrange(140, 200, 4); lost = round(sched * rng.uniform(0.15, 0.35))
        opts, ci = _pct_options(rng, 100 * lost / sched)
        return (f"An agent was scheduled {sched} hours this month; {lost} hours went to leave, training and breaks. Shrinkage = ?",
                opts, ci, CAT_KPI, "hard")
    makers.append(shrinkage)

    def deflection():
        selfsvc = rng.randrange(400, 4000, 100); agent = rng.randrange(300, 3000, 100)
        opts, ci = _pct_options(rng, 100 * selfsvc / (selfsvc + agent))
        return (f"This week {selfsvc} queries were resolved in self-service and {agent} needed an agent. Self-service deflection = ?",
                opts, ci, CAT_SS, "medium")
    makers.append(deflection)

    for i in range(count):
        q, opts, ci, cat, diff = makers[i % len(makers)]()
        rows.append(_mk(rng, q, opts, ci, cat, diff, timer=30))
    return rows


def _benefit_questions(rng) -> list[dict]:
    rows = []
    for topic, benefit, cat in BENEFITS:
        distr = rng.sample(FAKE_BENEFITS, 3)
        rows.append(_mk(rng, f"Which of the following is a genuine benefit of {topic}?",
                        [benefit.capitalize()] + [d.capitalize() for d in distr], 0, cat, "easy"))
        others = [b for t, b, c in BENEFITS if t != topic]
        distr2 = rng.sample(others, 3)
        rows.append(_mk(rng, f"The PRIMARY outcome you'd expect from investing in {topic} is:",
                        [benefit.capitalize()] + [d.capitalize() for d in distr2], 0, cat, "medium"))
    return rows


def _scenario_questions(rng) -> list[dict]:
    return [_mk(rng, q, opts, ci, cat, diff, timer=25) for q, opts, ci, cat, diff in SCENARIOS]


def _subjective_questions(rng) -> list[dict]:
    rows = []
    for s in SUBJECTIVE_SCENARIOS:
        rows.append(_mk(rng, s, None, 0, CAT_SUBJ, "medium", qtype="subjective", points=config.VOTE_POINTS))
    extras = [
        "In one line: what does great customer service FEEL like?",
        "Describe the worst IVR experience you can imagine — then flip it into the best.",
        "You get one Slack message to the whole team before Monday's rush. What do you write?",
        "Explain 'containment rate' to a 10-year-old.",
        "What's one thing AI should NEVER do in customer service?",
    ]
    for s in extras:
        rows.append(_mk(rng, s, None, 0, CAT_SUBJ, "easy", qtype="subjective", points=config.VOTE_POINTS))
    return rows


# ============================================================
# Public API
# ============================================================

def ensure_bank() -> None:
    """Generate question_bank.xlsx once (kept if it already exists)."""
    if config.QUESTION_BANK_XLSX.exists():
        return
    storage.ensure_data_dir()
    rng = random.Random(42)

    rows: list[dict] = []
    rows += _term_questions(rng)
    rows += _scenario_questions(rng)
    rows += _benefit_questions(rng)
    rows += _subjective_questions(rng)

    # top up with numeric KPI calculations to reach exactly QUESTION_BANK_SIZE
    seen = {r["question"] for r in rows}
    need = config.QUESTION_BANK_SIZE - len(rows)
    batch = _numeric_questions(rng, need + 400)  # extra to survive dedupe
    for r in batch:
        if len(rows) >= config.QUESTION_BANK_SIZE:
            break
        if r["question"] not in seen:
            seen.add(r["question"])
            rows.append(r)

    rng.shuffle(rows)
    rows = rows[:config.QUESTION_BANK_SIZE]
    for i, r in enumerate(rows, start=1):
        r["qid"] = f"QB{i:04d}"

    df = pd.DataFrame(rows)[BANK_COLS]
    with pd.ExcelWriter(config.QUESTION_BANK_XLSX, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="bank", index=False)


def load_bank() -> pd.DataFrame:
    ensure_bank()
    return pd.read_excel(config.QUESTION_BANK_XLSX, sheet_name="bank", engine="openpyxl")


def build_quiz_from_bank(title: str, emoji: str, categories: list[str], difficulties: list[str],
                         n_questions: int, subjective_count: int, created_by: str) -> str:
    """Sample questions from the bank into a hostable quiz. Returns quiz_id."""
    bank = load_bank()
    mcq = bank[(bank["qtype"] == "mcq") & bank["category"].isin(categories)]
    if difficulties:
        mcq = mcq[mcq["difficulty"].isin(difficulties)]
    subj = bank[bank["qtype"] == "subjective"]

    n_mcq = max(0, n_questions - subjective_count)
    picked = mcq.sample(n=min(n_mcq, len(mcq)), random_state=None)
    picked_subj = subj.sample(n=min(subjective_count, len(subj)), random_state=None)

    quiz_id = "bank-" + datetime.now().strftime("%y%m%d-%H%M%S")
    storage.add_quiz(quiz_id, title, emoji, " + ".join(categories)[:60] or "Mixed",
                     config.DEFAULT_TIMER_SEC, created_by)

    frames = pd.concat([picked, picked_subj]).sample(frac=1)  # shuffle order
    for _, r in frames.iterrows():
        storage.add_question(
            quiz_id, str(r["question"]),
            [str(r["opt_a"]), str(r["opt_b"]), str(r["opt_c"]), str(r["opt_d"])],
            str(r["correct"]) if r["qtype"] == "mcq" else "",
            int(r["timer_sec"]), int(r["points"]), qtype=str(r["qtype"]),
        )
    return quiz_id
