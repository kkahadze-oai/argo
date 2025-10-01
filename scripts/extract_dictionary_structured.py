"""
Extract Georgian multilingual dictionary in structured format
"""

import pytesseract
from doctr.io import DocumentFile
import numpy as np
from PIL import Image
import re
import csv
import json

def parse_dictionary_text(text):
    """Parse the OCR text into structured dictionary entries"""
    lines = text.strip().split('\n')
    
    # Find the header line
    header_found = False
    entries = []
    current_entry = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip the header lines
        if 'ქართული' in line and 'მეგრული' in line:
            header_found = True
            continue
        if 'Georgian' in line and 'Megrelian' in line:
            continue
            
        if not header_found:
            continue
            
        # Try to identify dictionary entries
        # Look for lines that start with Georgian words (no parentheses)
        if line and not line.startswith('(') and not line.startswith('13'):
            # This might be a new entry
            if current_entry:
                entries.append(current_entry)
            
            # Split the line into columns (rough approximation)
            parts = re.split(r'\s{2,}|\t', line)  # Split on multiple spaces or tabs
            
            current_entry = {
                'georgian': '',
                'megrelian': '',
                'laz': '',
                'svan': '',
                'english': '',
                'georgian_forms': '',
                'megrelian_forms': '',
                'laz_forms': '',
                'svan_forms': ''
            }
            
            # Try to extract the main word and its translations
            if len(parts) >= 5:
                current_entry['georgian'] = parts[0]
                current_entry['megrelian'] = parts[1] 
                current_entry['laz'] = parts[2]
                current_entry['svan'] = parts[3]
                current_entry['english'] = ' '.join(parts[4:])
            elif len(parts) >= 1:
                current_entry['georgian'] = parts[0]
                # Try to extract English from the end
                english_match = re.search(r'(to \w+.*|bath|bag|tinder|web|silk|armor|bower|here|August)', line)
                if english_match:
                    current_entry['english'] = english_match.group(1)
        
        elif line.startswith('(') and current_entry:
            # This is likely grammatical forms
            # Try to split into columns
            forms = re.split(r'\s{2,}|\t', line)
            if len(forms) >= 1:
                current_entry['georgian_forms'] = forms[0]
            if len(forms) >= 2:
                current_entry['megrelian_forms'] = forms[1]
            if len(forms) >= 3:
                current_entry['laz_forms'] = forms[2]
            if len(forms) >= 4:
                current_entry['svan_forms'] = forms[3]
    
    # Add the last entry
    if current_entry:
        entries.append(current_entry)
    
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
    entries = parse_dictionary_text(text)
    
    return entries, text

def main():
    entries, raw_text = extract_page_dictionary(14)
    
    print(f"\n=== Extracted {len(entries)} dictionary entries ===\n")
    
    # Display entries in a nice format
    for i, entry in enumerate(entries, 1):
        print(f"{i}. Georgian: {entry['georgian']}")
        if entry['megrelian']:
            print(f"   Megrelian: {entry['megrelian']}")
        if entry['laz']:
            print(f"   Laz: {entry['laz']}")
        if entry['svan']:
            print(f"   Svan: {entry['svan']}")
        if entry['english']:
            print(f"   English: {entry['english']}")
        if entry['georgian_forms']:
            print(f"   Georgian forms: {entry['georgian_forms']}")
        print()
    
    # Save to CSV
    csv_filename = "dictionary_page_14.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['georgian', 'megrelian', 'laz', 'svan', 'english', 
                     'georgian_forms', 'megrelian_forms', 'laz_forms', 'svan_forms']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
    
    print(f"Saved to {csv_filename}")
    
    # Save raw text
    with open("dictionary_page_14_raw.txt", 'w', encoding='utf-8') as f:
        f.write(raw_text)
    
    print("Saved raw OCR text to dictionary_page_14_raw.txt")
    
    # Save as JSON for easier processing
    with open("dictionary_page_14.json", 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    
    print("Saved structured data to dictionary_page_14.json")

if __name__ == "__main__":
    main() 