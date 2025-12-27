import json
import os, sys
import time
from playwright.sync_api import sync_playwright

def capture_screenshots(json_file):
    output_dir = "screenshots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            courses = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {json_file}. Run the scraper first.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        print(f"Starting screenshot capture for {len(courses)} courses...")

        for course in courses:
            lesson_code = course.get("data-lesson-code", "UNKNOWN")
            url = course.get("detail_link")

            safe_filename = "".join(c for c in lesson_code if c.isalnum() or c in (' ', '-', '_')).strip()
            file_path = os.path.join(output_dir, f"{safe_filename}.png")

            if not url:
                print(f"Skipping {lesson_code}: No URL found.")
                continue

            print(f"Capturing: {lesson_code}...")

            try:
                page.goto(url, wait_until="networkidle", timeout=60000)

                page.screenshot(path=file_path, full_page=True)

            except Exception as e:
                print(f"Failed to capture {lesson_code}: {e}")

        browser.close()
        print("All screenshots captured.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python screenshots.py <json_file_name>")
        sys.exit(1)

    filename =  sys.argv[1]
    capture_screenshots(filename)