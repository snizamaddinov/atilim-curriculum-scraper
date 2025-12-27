import json
import os
import sys
from pypdf import PdfWriter, PdfReader

def merge_pdfs_ordered(json_file_path, pdf_folder, output_filename):
    # 1. Load the JSON to get the correct order
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            courses = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file_path}' not found.")
        sys.exit(1)

    writer = PdfWriter()
    count = 0

    print(f"Merging PDFs from '{pdf_folder}' based on order in '{json_file_path}'...")

    # 2. Iterate through JSON to preserve order
    for course in courses:
        lesson_code = course.get("data-lesson-code", "UNKNOWN")
        
        # Reconstruct the filename using the same logic as the generator script
        safe_filename = "".join(c for c in lesson_code if c.isalnum() or c in (' ', '-', '_')).strip()
        pdf_path = os.path.join(pdf_folder, f"{safe_filename}.pdf")

        if os.path.exists(pdf_path):
            try:
                # Append the PDF to the writer
                writer.append(pdf_path)
                count += 1
                print(f"[{count}] Added: {lesson_code}")
            except Exception as e:
                print(f"Error reading {lesson_code}: {e}")
        else:
            print(f"Warning: File not found for {lesson_code} ({pdf_path})")

    if count == 0:
        print("No files were merged. Exiting.")
        return

    # 3. Compression & Optimization
    print("\nOptimizing file size (this may take a moment)...")
    
    # This removes duplicate objects (like fonts/logos shared across pages)
    # remove_identicals=True: Merges identical objects into one
    # remove_orphans=True: Removes objects not referenced by any page
    writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

    # 4. Save the Result
    try:
        with open(output_filename, "wb") as f:
            # pypdf automatically compresses content streams when writing
            writer.write(f)
        
        file_size_mb = os.path.getsize(output_filename) / (1024 * 1024)
        print(f"\nSuccess! Merged {count} files into '{output_filename}'.")
        print(f"Final File Size: {file_size_mb:.2f} MB")
        
    except Exception as e:
        print(f"Error writing final PDF: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python merger.py <json_file> <pdf_folder> <output_filename>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    folder_path = sys.argv[2]
    out_file = sys.argv[3]
    
    merge_pdfs_ordered(json_path, folder_path, out_file)