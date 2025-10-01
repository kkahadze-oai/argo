"""
Final Georgian multilingual dictionary extractor with proper column parsing
Georgian | Megrelian | Laz | Svan | English
"""

import pytesseract
from doctr.io import DocumentFile
import numpy as np
from PIL import Image
import re
import csv
import json

def parse_dictionary_line(line):
    """Parse a single dictionary line into 5 columns"""
    # Remove extra whitespace
    line = re.sub(r'\s+', ' ', line.strip())
    
    # First, extract the English part (usually at the end)
    english_patterns = [
        r'\b(to \w+[^a-zA-Z]*(?:\([^)]*\))?[^a-zA-Z]*(?:make|will|up|excite|tousle|blister|crawl|smoke|wave|ignite|stand|throw|construct|blaze|roll)[^a-zA-Z]*(?:\w+)*)',
        r'\b(bath-house|old \d+ kopecks|bath|bag|tinder|web|silk|armor|bower|here|August)'
    ]
    
    english_part = ""
    georgian_part = line
    
    for pattern in english_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            english_part = match.group(1).strip()
            georgian_part = line[:match.start()].strip()
            break
    
    # Now split the Georgian part
    # Remove common OCR artifacts and extra info
    georgian_part = re.sub(r'\s*\|\s*', ' ', georgian_part)  # Remove | separators
    georgian_part = re.sub(r'\s*_\s*', ' ', georgian_part)   # Remove _ separators
    georgian_part = re.sub(r'რუს\.\s*', '', georgian_part)   # Remove "რუს." (Russian)
    georgian_part = re.sub(r'თურქ\.\s*', '', georgian_part)  # Remove "თურქ." (Turkish)
    
    # Split on multiple spaces (2 or more)
    parts = re.split(r'\s{2,}', georgian_part)
    parts = [part.strip() for part in parts if part.strip()]
    
    # If we don't have enough parts, try splitting on single spaces but be more careful
    if len(parts) < 4:
        # Look for Georgian script patterns to identify word boundaries
        words = georgian_part.split()
        georgian_words = []
        current_word = []
        
        for word in words:
            if any(c in word for c in 'აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ'):
                if current_word:
                    georgian_words.append(' '.join(current_word))
                    current_word = []
                current_word.append(word)
            else:
                if current_word:
                    current_word.append(word)
        
        if current_word:
            georgian_words.append(' '.join(current_word))
        
        parts = georgian_words
    
    # Ensure we have exactly 4 parts for the Georgian languages
    while len(parts) < 4:
        parts.append('')
    
    return {
        'georgian': parts[0] if len(parts) > 0 else '',
        'megrelian': parts[1] if len(parts) > 1 else '',
        'laz': parts[2] if len(parts) > 2 else '',
        'svan': parts[3] if len(parts) > 3 else '',
        'english': english_part
    }

def parse_dictionary_table(text):
    """Parse the OCR text into 5-column table structure"""
    lines = text.strip().split('\n')
    
    entries = []
    header_found = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip headers and page numbers
        if any(x in line for x in ['ქართული', 'Georgian', '13', 'ა']):
            if 'ქართული' in line:
                header_found = True
            continue
            
        if not header_found:
            continue
        
        # Skip lines that are clearly grammatical forms (start with parentheses)
        if line.startswith('('):
            continue
            
        # Skip lines that don't contain Georgian script
        if not any(c in line for c in 'აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ'):
            continue
        
        # Parse the line
        entry = parse_dictionary_line(line)
        
        # Clean up entries
        for key in entry:
            if entry[key]:
                # Remove trailing punctuation and artifacts
                entry[key] = re.sub(r'[|_\-,]+$', '', entry[key]).strip()
                # Remove leading/trailing parentheses if they're artifacts
                entry[key] = re.sub(r'^\([^)]*\)$', '', entry[key]).strip()
        
        # Only add if we have at least Georgian and some other content
        if entry['georgian'] and (entry['english'] or entry['megrelian'] or entry['laz'] or entry['svan']):
            entries.append(entry)
    
    return entries

def extract_page_dictionary(page_num=14):
    """Extract dictionary from a specific page"""
    print(f"Loading PDF...")
    all_pages = DocumentFile.from_pdf("data/qarTul_megrul_lazur_svanur_inglisuri_leq.pdf")
    
    if len(all_pages) <= page_num - 1:
        print(f"PDF only has {len(all_pages)} pages, but you requested page {page_num}")
        return []
    
    page_image = all_pages[page_num - 1]
    print(f"Processing page {page_num} of {len(all_pages)} pages")
    
    # Convert numpy array to PIL Image
    if page_image.dtype != np.uint8:
        page_image = (page_image * 255).astype(np.uint8)
    
    pil_image = Image.fromarray(page_image)
    
    # Perform OCR with Georgian + English
    print("Running OCR...")
    text = pytesseract.image_to_string(pil_image, lang='kat+eng')
    
    # Parse into structured format
    entries = parse_dictionary_table(text)
    
    return entries, text

def main():
    entries, raw_text = extract_page_dictionary(14)
    
    print(f"\n=== Extracted {len(entries)} dictionary entries ===\n")
    
    # Display entries in a nice table format
    print(f"{'Georgian':<20} {'Megrelian':<20} {'Laz':<15} {'Svan':<15} {'English':<30}")
    print("-" * 100)
    
    for entry in entries:
        georgian = entry['georgian'][:19] if len(entry['georgian']) > 19 else entry['georgian']
        megrelian = entry['megrelian'][:19] if len(entry['megrelian']) > 19 else entry['megrelian']
        laz = entry['laz'][:14] if len(entry['laz']) > 14 else entry['laz']
        svan = entry['svan'][:14] if len(entry['svan']) > 14 else entry['svan']
        english = entry['english'][:29] if len(entry['english']) > 29 else entry['english']
        
        print(f"{georgian:<20} {megrelian:<20} {laz:<15} {svan:<15} {english:<30}")
    
    # Save to CSV
    csv_filename = "dictionary_page_14_final.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['georgian', 'megrelian', 'laz', 'svan', 'english']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
    
    print(f"\nSaved to {csv_filename}")
    
    # Save as JSON
    with open("dictionary_page_14_final.json", 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    
    print("Saved structured data to dictionary_page_14_final.json")

if __name__ == "__main__":
    main() 