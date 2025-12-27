import json
import os
from playwright.sync_api import sync_playwright

def generate_desktop_pdfs(json_file="compe_curriculum.json"):
    output_dir = "course_pdfs_screen2"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            courses = json.load(f)
    except FileNotFoundError:
        print("JSON file not found.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # 1. Set explicit viewport size (Desktop width)
        # This prevents the site from collapsing into mobile/tablet mode.
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1 
        )
        page = context.new_page()

        print(f"Generating Desktop Layout PDFs for {len(courses)} courses...")

        for course in courses:
            lesson_code = course.get("data-lesson-code", "UNKNOWN")
            url = course.get("detail_link")
            
            safe_filename = "".join(c for c in lesson_code if c.isalnum() or c in (' ', '-', '_')).strip()
            pdf_path = os.path.join(output_dir, f"{safe_filename}.pdf")

            if not url:
                continue

            print(f"Processing: {lesson_code}...")

            try:
                page.goto(url, wait_until="domcontentloaded")

                # 2. Force Screen Media
                # Renders colors and layout exactly as seen on a monitor
                page.emulate_media(media="screen")

                # 3. Clean up the page (Optional but recommended)
                # Removes the footer or header if they overlay content in the PDF
                # page.evaluate("""() => {
                #     // Example: Remove fixed headers that might block text
                #     const header = document.querySelector('header');
                #     if (header) header.style.position = 'static';
                # }""")

                # 4. Generate PDF
                # 'width' helps map the 1920px content onto paper.
                # If content is cut off, we can scale it down.
                page.pdf(
                    path=pdf_path,
                    format="A4",
                    print_background=True,
                    margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"},
                    scale=0.65  # Scales the 1920px view to fit onto A4 paper
                )

            except Exception as e:
                print(f"Failed to process {lesson_code}: {e}")

        browser.close()
        print(f"All PDFs saved to '{output_dir}/'.")

if __name__ == "__main__":
    generate_desktop_pdfs()