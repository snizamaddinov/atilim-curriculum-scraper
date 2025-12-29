import json
import requests
import sys
from bs4 import BeautifulSoup

def scrape_course_details(json_file_path):
    output_filename = 'scraped_courses.json'
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            course_list = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    extracted_data = []

    print(f"Starting scrape for {len(course_list)} courses...")

    for item in course_list:
        course_code = item.get('data-lesson-code', 'Unknown')
        detail_link = item.get('detail_link')

        if not detail_link:
            print(f"Skipping {course_code}: No detail link provided.")
            continue

        try:
            response = requests.get(detail_link)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')

            container = soup.find('div', class_='detail-container ects')
            
            if not container:
                print(f"Warning: 'detail-container ects' not found for {course_code}")
                continue

            col_divs = container.find_all('div', class_='col-md-12')

            title = "N/A"
            if len(col_divs) > 0:
                h1_tag = col_divs[0].find('h1')
                if h1_tag:
                    raw_title = h1_tag.get_text(strip=True)
                    title = raw_title.replace("Course Detail", "").strip()

            table_details = {}
            if len(col_divs) > 1:
                target_div = col_divs[1]
                table = target_div.find('table')
                
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        th = row.find('th')
                        td = row.find('td')
                        
                        if th and td:
                            key = th.get_text(strip=True)
                            value = td.get_text(separator=" ", strip=True)
                            table_details[key] = value

            course_data = {
                "course_code": course_code,
                "title": title,
                "details": table_details
            }
            
            extracted_data.append(course_data)
            print(f"Scraped: {course_code}")

        except Exception as e:
            print(f"Error scraping {course_code}: {e}")

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)

    print(f"\nScraping complete. Data saved to '{output_filename}'")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        scrape_course_details(sys.argv[1])
    else:
        print("Please provide the JSON file name as a parameter.")