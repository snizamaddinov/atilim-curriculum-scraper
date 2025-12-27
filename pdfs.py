import json
import os
import sys
from playwright.sync_api import sync_playwright

def generate_pdfs(json_file_path, output_folder_name):
    if not os.path.exists(output_folder_name):
        os.makedirs(output_folder_name)
        print(f"Created directory: {output_folder_name}")

    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            courses = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file_path}' not found.")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1
        )
        page = context.new_page()

        print(f"Generating PDFs for {len(courses)} courses into '{output_folder_name}'...")

        for course in courses:
            lesson_code = course.get("data-lesson-code", "UNKNOWN")
            url = course.get("detail_link")

            safe_filename = "".join(c for c in lesson_code if c.isalnum() or c in (' ', '-', '_')).strip()
            pdf_path = os.path.join(output_folder_name, f"{safe_filename}.pdf")

            if not url:
                continue

            print(f"Processing: {lesson_code}...")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)

                # 4. Remove Header, Footer, and Sidebar
                page.evaluate("""() => {
                    const remove = (sel) => {
                        const el = document.querySelector(sel);
                        if (el) el.remove();
                    };

                    remove('header');              // Remove <header> tags
                    remove('footer');              // Remove <footer> tags
                    remove('.sidebar-container');  // Remove specific class

                    // Optional: Remove any fixed bottom/top bars that might persist
                    document.body.style.paddingTop = '0px';
                    document.body.style.paddingBottom = '0px';
                }""")

                page.emulate_media(media="screen")

                # Scale is set to 0.65 to fit the 1920px viewport onto an A4 page width
                page.pdf(
                    path=pdf_path,
                    format="A4",
                    print_background=True,
                    margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"},
                    scale=0.65 
                )

            except Exception as e:
                print(f"Failed to process {lesson_code}: {e}")

        browser.close()
        print("Job done.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pdf.py <input_json> <output_folder>")
        sys.exit(1)

    input_json = sys.argv[1]
    output_folder = sys.argv[2]

    generate_pdfs(input_json, output_folder)
