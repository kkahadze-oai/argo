"""
Extract Georgian multilingual dictionary table with proper 5-column structure
Georgian | Megrelian | Laz | Svan | English
"""

import pytesseract
from doctr.io import DocumentFile
import numpy as np
from PIL import Image
import re
import csv
import json

def parse_dictionary_table(text):
    """Parse the OCR text into 5-column table structure"""
    lines = text.strip().split('\n')
    
    entries = []
    header_found = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip the Georgian header line
        if 'ქართული' in line and 'მეგრული' in line:
            header_found = True
            continue
        # Skip the English header line  
        if 'Georgian' in line and 'Megrelian' in line:
            continue
        # Skip page numbers
        if line == '13' or line == 'ა':
            continue
            
        if not header_found:
            continue
        
        # Skip lines that are clearly grammatical forms (start with parentheses)
        if line.startswith('('):
            continue
            
        # Try to parse as a table row
        # Look for lines that contain dictionary entries
        if any(georgian_char in line for georgian_char in 'აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ'):
            
            # Try to split the line into 5 columns
            # First, let's identify the English part (usually starts with "to" or common English words)
            english_pattern = r'(to \w+.*|bath|bag|tinder|web|silk|armor|bower|here|August|old \d+ kopecks)'
            english_match = re.search(english_pattern, line)
            
            if english_match:
                english_part = english_match.group(1)
                # Remove the English part to work with the rest
                georgian_part = line[:english_match.start()].strip()
            else:
                english_part = ""
                georgian_part = line
            
            # Now try to split the Georgian part into 4 columns
            # Split on multiple spaces (2 or more spaces typically separate columns)
            parts = re.split(r'\s{2,}', georgian_part)
            
            # Clean up parts
            parts = [part.strip() for part in parts if part.strip()]
            
            if len(parts) >= 1:  # At least Georgian word
                entry = {
                    'georgian': parts[0] if len(parts) > 0 else '',
                    'megrelian': parts[1] if len(parts) > 1 else '',
                    'laz': parts[2] if len(parts) > 2 else '',
                    'svan': parts[3] if len(parts) > 3 else '',
                    'english': english_part
                }
                
                # Clean up entries - remove obvious OCR artifacts
                for key in entry:
                    if entry[key]:
                        # Remove trailing punctuation that might be OCR errors
                        entry[key] = re.sub(r'[|_\-]+$', '', entry[key]).strip()
                
                # Only add if we have at least Georgian and English
                if entry['georgian'] and (entry['english'] or entry['megrelian']):
                    entries.append(entry)
    
    return entries

def extract_page_dictionary(page_num=14):
    """Extract dictionary from a specific page"""
    print(f"Loading PDF...")
    all_pages = DocumentFile.from_pdf("data/qarTul_megrul_lazur_svanur_inglisuri_leq.pdf")
    
    if len(all_pages) <= page_num - 1:
        print(f"PDF only has {len(all_pages)} pages, but you requested page {page_num}")
        return []
    
    page_image = all_pages[page_num - 1]  # Convert to 0-based index
    print(f"Processing page {page_num} of {len(all_pages)} pages")
    
    # Convert numpy array to PIL Image
    if page_image.dtype != np.uint8:
        page_image = (page_image * 255).astype(np.uint8)
    
    pil_image = Image.fromarray(page_image)
    
    # Perform OCR with Georgian + English
    print("Running OCR...")
    text = pytesseract.image_to_string(pil_image, lang='kat+eng')
    
    print("Raw OCR text:")
    print("=" * 50)
    print(text)
    print("=" * 50)
    
    # Parse into structured format
    entries = parse_dictionary_table(text)
    
    return entries, text

def main():
    entries, raw_text = extract_page_dictionary(14)
    
    print(f"\n=== Extracted {len(entries)} dictionary entries ===\n")
    
    # Display entries in a nice table format
    print(f"{'Georgian':<15} {'Megrelian':<15} {'Laz':<15} {'Svan':<15} {'English':<25}")
    print("-" * 85)
    
    for entry in entries:
        print(f"{entry['georgian']:<15} {entry['megrelian']:<15} {entry['laz']:<15} {entry['svan']:<15} {entry['english']:<25}")
    
    # Save to CSV
    csv_filename = "dictionary_page_14_table.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['georgian', 'megrelian', 'laz', 'svan', 'english']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
    
    print(f"\nSaved to {csv_filename}")
    
    # Save as JSON for easier processing
    with open("dictionary_page_14_table.json", 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    
    print("Saved structured data to dictionary_page_14_table.json")

if __name__ == "__main__":
    main() 