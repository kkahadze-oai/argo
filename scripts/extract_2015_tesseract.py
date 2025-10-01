"""
Tesseract OCR for Georgian text recognition
Requires: pip install pytesseract
And tesseract with Georgian language data installed
"""

import pytesseract
from doctr.io import DocumentFile
import numpy as np
from PIL import Image

def main():
    # Load all pages from PDF first
    print("Loading PDF...")
    all_pages = DocumentFile.from_pdf("data/qarTul_megrul_lazur_svanur_inglisuri_leq.pdf")
    
    # Select only page 14 (index 13 because it's 0-based)
    if len(all_pages) > 13:
        page_image = all_pages[13]  # Get page 14
        print(f"Processing page 14 of {len(all_pages)} pages")
    else:
        print(f"PDF only has {len(all_pages)} pages, but you requested page 14")
        return
    
    # Convert numpy array to PIL Image
    if page_image.dtype != np.uint8:
        page_image = (page_image * 255).astype(np.uint8)
    
    pil_image = Image.fromarray(page_image)
    
    # Try different language configurations
    language_configs = [
        ('kat', 'Georgian only'),
        ('kat+eng', 'Georgian + English'),
        ('eng', 'English only (for comparison)'),
    ]
    
    for lang_code, description in language_configs:
        print(f"\n=== Testing {description} ({lang_code}) ===")
        try:
            # Perform OCR with Tesseract
            text = pytesseract.image_to_string(pil_image, lang=lang_code)
            
            if text.strip():
                print("OCR Result:")
                print(text)
            else:
                print("No text detected")
                
        except Exception as e:
            print(f"Error with {lang_code}: {e}")
            if "kat" in lang_code:
                print("Georgian language data might not be installed.")
                print("Try: brew install tesseract-lang (on macOS)")
                print("Or download from: https://github.com/tesseract-ocr/tessdata")

if __name__ == "__main__":
    main() 