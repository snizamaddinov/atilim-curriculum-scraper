import json
import os
from playwright.sync_api import sync_playwright

def generate_pdfs(json_file="compe_curriculum.json"):
    # 1. Create output directory
    output_dir = "course_pdfs_screen"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Load data
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            courses = json.load(f)
    except FileNotFoundError:
        print("JSON file not found.")
        return

    with sync_playwright() as p:
        # PDF generation ONLY works in headless mode
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"Generating PDFs for {len(courses)} courses...")

        for course in courses:
            lesson_code = course.get("data-lesson-code", "UNKNOWN")
            url = course.get("detail_link")
            
            # Clean filename
            safe_filename = "".join(c for c in lesson_code if c.isalnum() or c in (' ', '-', '_')).strip()
            pdf_path = os.path.join(output_dir, f"{safe_filename}.pdf")

            if not url:
                continue

            print(f"Processing: {lesson_code}...")

            try:
                # Go to page
                page.goto(url, wait_until="domcontentloaded")

                # --- THE MAGIC STEP ---
                # This forces the browser to render the page using the "Print" CSS 
                # exactly like DevTools -> Rendering -> Emulate CSS media: print
                page.emulate_media(media="screen")

                # Generate the PDF
                # format="A4": Standard paper size
                # print_background=True: Keeps colors/shading in tables (important for curriculums)
                # margin: Adds whitespace so text doesn't hit the edge
                page.pdf(
                    path=pdf_path,
                    format="A4",
                    print_background=True,
                    margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"}
                )

            except Exception as e:
                print(f"Failed to process {lesson_code}: {e}")

        browser.close()
        print(f"All PDFs saved to '{output_dir}/'.")

if __name__ == "__main__":
    generate_pdfs()