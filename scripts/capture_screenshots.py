#!/usr/bin/env python3
"""
Capture all "screens" of a web page (viewport-sized screenshots while scrolling)
and save them to a directory.
Usage:
  python scripts/capture_screenshots.py [URL] [--output DIR]
  Default URL: http://127.0.0.1:8000/
  Default output: screenshots/
"""
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Capture viewport screenshots of a page.")
    parser.add_argument("url", nargs="?", default="http://127.0.0.1:8000/", help="Page URL")
    parser.add_argument("--output", "-o", default="screenshots", help="Output directory")
    parser.add_argument("--viewport-width", type=int, default=1280, help="Viewport width")
    parser.add_argument("--viewport-height", type=int, default=720, help="Viewport height")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)
    base_url = args.url if args.url.startswith("http") else f"http://{args.url}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": args.viewport_width, "height": args.viewport_height},
            ignore_https_errors=True,
        )
        page = context.new_page()
        try:
            page.goto(base_url, wait_until="networkidle", timeout=15000)
        except Exception as e:
            print(f"Could not load {base_url}: {e}")
            print("Make sure the dev server is running (e.g. python manage.py runserver).")
            browser.close()
            sys.exit(2)

        # Get total scroll height
        total_height = page.evaluate("document.documentElement.scrollHeight")
        viewport_height = args.viewport_height
        n_screens = max(1, (total_height + viewport_height - 1) // viewport_height)

        for i in range(n_screens):
            scroll_y = i * viewport_height
            page.evaluate(f"window.scrollTo(0, {scroll_y})")
            page.wait_for_timeout(300)  # allow any scroll animations
            path = os.path.join(args.output, f"screenshot_{i + 1:02d}.png")
            page.screenshot(path=path)
            print(f"Saved {path}")

        browser.close()

    print(f"Done. Saved {n_screens} screenshot(s) to {args.output}/")


if __name__ == "__main__":
    main()
