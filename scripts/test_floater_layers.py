"""Verify floating symbols sit behind UI text after login."""
import sys
import time

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP: playwright not installed")
    sys.exit(0)


def check_layers(page, label: str) -> dict:
    result = page.evaluate(
        """() => {
            const host = document.querySelector('[data-testid="stAppViewContainer"]');
            const wrap = document.getElementById('qt-floaters');
            const text = document.querySelector(
                '[data-testid="stMarkdownContainer"] p, [data-testid="stTextInput"] label, .qt-brand, h1, h2, h3'
            );
            const floater = document.querySelector('.qt-floater');
            function z(el) {
                if (!el) return null;
                return parseInt(getComputedStyle(el).zIndex, 10) || 0;
            }
            function pos(el) {
                if (!el) return null;
                return getComputedStyle(el).position;
            }
            const main = host && host.querySelector('section.main, [data-testid="stMain"]');
            return {
                host: !!host,
                wrapParent: wrap && host ? wrap.parentElement === host : false,
                wrapFirst: wrap && host ? host.firstChild === wrap : false,
                wrapPos: pos(wrap),
                wrapZ: z(wrap),
                mainZ: z(main),
                textZ: z(text),
                floaterZ: z(floater),
                ok: !!(wrap && host && wrap.parentElement === host && host.firstChild === wrap
                    && pos(wrap) === 'absolute' && z(wrap) <= z(main))
            };
        }"""
    )
    result["label"] = label
    return result


def main() -> int:
    url = "http://localhost:8502"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=60000)
        time.sleep(2)
        login = check_layers(page, "login")
        print("LOGIN:", login)

        # Admin login
        page.get_by_role("tab", name="Admin").click()
        time.sleep(0.5)
        admin_panel = page.get_by_role("tabpanel", name="Admin")
        admin_panel.get_by_placeholder("you@abc.com").fill("admin@abc.com")
        admin_panel.locator('input[type="password"]').fill("admin123")
        page.get_by_role("button", name="Enter Command Center").click()
        time.sleep(5)  # transition + admin load
        admin = check_layers(page, "admin")
        print("ADMIN:", admin)

        browser.close()
        if login.get("ok") and admin.get("ok"):
            print("PASS: floaters behind UI on login and admin")
            return 0
        print("FAIL: floater layer check failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
