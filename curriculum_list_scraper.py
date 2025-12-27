import requests
from bs4 import BeautifulSoup
import json
import time
import sys
from urllib.parse import urlparse

def scrape_curriculum(base_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    parsed_url = urlparse(base_url)
    path_segments = parsed_url.path.strip("/").split("/")

    if len(path_segments) >= 2:
        dept_name = path_segments[1]
        output_file = f"{dept_name}_curriculum.json"
    else:
        output_file = "curriculum.json"

    print(f"Target URL: {base_url}")
    print(f"Output will be saved to: {output_file}")

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve page: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    lesson_cards = soup.find_all('a', class_='lesson_card')
    print(f"Found {len(lesson_cards)} lesson cards.")

    courses_data = []

    for card in lesson_cards:
        lesson_code = card.get_text(strip=True)
        curriculum_id = card.get('data-circulum-id')

        if not lesson_code or not curriculum_id:
            continue

        print(f"Processing {lesson_code} (ID: {curriculum_id})...")

        api_url = f"https://www.atilim.edu.tr/get-lesson-ects/{lesson_code}/{curriculum_id}"

        try:
            detail_response = requests.get(api_url, headers=headers)
            raw_link = detail_response.text.strip()

            if "atilim.edu.tr/" in raw_link and "/en/" not in raw_link:
                final_link = raw_link.replace("atilim.edu.tr/", "atilim.edu.tr/en/")
            else:
                final_link = raw_link 

            course_obj = {
                "data-lesson-code": lesson_code,
                "data-circulum-id": curriculum_id,
                "detail_link": final_link
            }

            courses_data.append(course_obj)

        except Exception as e:
            print(f"Error fetching details for {lesson_code}: {e}")

        time.sleep(0.5)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(courses_data, f, indent=4, ensure_ascii=False)

    print(f"Scraping complete. Data saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <URL>")
        sys.exit(1)

    url_arg = sys.argv[1]
    scrape_curriculum(url_arg)