#!/usr/bin/env python3
"""
Capture screenshots of EVERY frontend page. Logs in if possible, resolves
dynamic IDs (app_id, run_id, developer name), then captures each page
(viewport-sized screenshots while scrolling). Saves to screenshots/<page_slug>/.
"""
import argparse
import os
import re
import sys
from urllib.parse import quote

try:
    import requests
except ImportError:
    requests = None

# All frontend routes (path, slug for folder name). Dynamic segments filled later.
ROUTES = [
    ("", "landing"),
    ("login/", "login"),
    ("register/", "register"),
    ("dashboard/", "dashboard"),
    ("apps/{app_id}/", "app-detail"),
    ("analysis/", "analysis-history"),
    ("analysis/{run_id}/", "analysis-detail"),
    ("profile/", "profile"),
    ("compare/", "compare"),
    ("watchlist/", "watchlist"),
    ("insights/", "insights"),
    ("developer/{developer_name}/", "developer-profile"),
    ("learn/", "learn"),
    ("reports/", "community-reports"),
]

# Credentials to try for login (so we can capture authenticated views)
LOGIN_CREDS = [
    ("testuser", "testpass123"),
    ("test", "test@123"),
]


def slugify(s: str) -> str:
    """Safe folder name from a string."""
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"[-\s]+", "-", s).strip("-") or "unknown"


def fetch_dynamic_ids(base_url: str, access_token: str | None):
    """Get first app_id, run_id, developer name from API. Returns dict."""
    ids = {"app_id": 1, "run_id": 1, "developer_name": "Unknown Developer"}
    if not requests or not access_token:
        return ids
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    try:
        r = requests.get(f"{base_url}/api/apps/", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", data) if isinstance(data, dict) else data
            if isinstance(results, list) and results:
                ids["app_id"] = results[0].get("id", 1)
    except Exception:
        pass
    try:
        r = requests.get(f"{base_url}/api/analysis/", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", data) if isinstance(data, dict) else data
            if isinstance(results, list) and results:
                ids["run_id"] = results[0].get("id", 1)
    except Exception:
        pass
    try:
        r = requests.get(f"{base_url}/api/insights/developers/", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", data) if isinstance(data, dict) else data
            if isinstance(results, list) and results:
                name = results[0].get("name") or results[0].get("developer")
                if name:
                    ids["developer_name"] = str(name)
    except Exception:
        pass
    return ids


def login(base_url: str) -> tuple[str | None, str | None]:
    """Return (access_token, refresh_token) or (None, None)."""
    if not requests:
        return None, None
    for username, password in LOGIN_CREDS:
        try:
            r = requests.post(
                f"{base_url}/api/auth/token/",
                json={"username": username, "password": password},
                timeout=10,
            )
            if r.status_code == 200:
                d = r.json()
                return d.get("access"), d.get("refresh")
        except Exception:
            continue
    return None, None


def main():
    parser = argparse.ArgumentParser(description="Capture all frontend pages.")
    parser.add_argument("--base", default="http://127.0.0.1:8000", help="Base URL")
    parser.add_argument("--output", "-o", default="screenshots", help="Output directory")
    parser.add_argument("--viewport-width", type=int, default=1280)
    parser.add_argument("--viewport-height", type=int, default=720)
    args = parser.parse_args()
    base_url = args.base.rstrip("/")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. Run: uv pip install playwright && playwright install chromium")
        sys.exit(1)

    # Login and resolve dynamic IDs
    access_token, refresh_token = login(base_url)
    if access_token:
        print("Logged in successfully.")
    else:
        print("Could not log in; capturing pages as anonymous.")
    dynamic = fetch_dynamic_ids(base_url, access_token)
    print(f"Dynamic IDs: app_id={dynamic['app_id']}, run_id={dynamic['run_id']}, developer={dynamic['developer_name']!r}")

    # Build list of (url_path, slug)
    pages = []
    for path_tpl, slug in ROUTES:
        path = path_tpl.format(
            app_id=dynamic["app_id"],
            run_id=dynamic["run_id"],
            developer_name=quote(dynamic["developer_name"], safe=""),
        )
        path = path or ""  # landing is ""
        pages.append((path, slug))

    os.makedirs(args.output, exist_ok=True)
    viewport_height = args.viewport_height

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": args.viewport_width, "height": viewport_height},
            ignore_https_errors=True,
        )
        page = context.new_page()

        # Inject auth so frontend sees us as logged in
        if access_token:
            def set_storage():
                page.goto(f"{base_url}/login/", wait_until="domcontentloaded", timeout=15000)
                page.evaluate(
                    """([access, refresh]) => {
                    localStorage.setItem('fad_access', access);
                    if (refresh) localStorage.setItem('fad_refresh', refresh);
                }""",
                    [access_token, refresh_token or ""],
                )
            set_storage()

        for url_path, slug in pages:
            url = f"{base_url}/{url_path}" if url_path else f"{base_url}/"
            out_dir = os.path.join(args.output, slug)
            os.makedirs(out_dir, exist_ok=True)
            try:
                page.goto(url, wait_until="networkidle", timeout=15000)
            except Exception as e:
                print(f"  [SKIP] {slug}: could not load - {e}")
                continue
            page.wait_for_timeout(500)

            total_height = page.evaluate("document.documentElement.scrollHeight")
            n_screens = max(1, (total_height + viewport_height - 1) // viewport_height)

            for i in range(n_screens):
                scroll_y = i * viewport_height
                page.evaluate(f"window.scrollTo(0, {scroll_y})")
                page.wait_for_timeout(200)
                path = os.path.join(out_dir, f"screenshot_{i + 1:02d}.png")
                page.screenshot(path=path)
            print(f"  [OK] {slug}: {n_screens} screenshot(s) -> {out_dir}")

        browser.close()

    print(f"\nDone. All pages saved under {args.output}/")


if __name__ == "__main__":
    main()
