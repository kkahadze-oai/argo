"""
EasyOCR for Georgian text recognition
Requires: pip install easyocr
"""

import easyocr
from doctr.io import DocumentFile
import numpy as np

def main():
    # Initialize EasyOCR reader with Georgian and English support
    print("Initializing EasyOCR with Georgian support...")
    reader = easyocr.Reader(['ka', 'en'])  # ka = Georgian, en = English
    
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
    
    # Perform OCR with EasyOCR
    print("Running EasyOCR...")
    try:
        # EasyOCR expects uint8 images
        if page_image.dtype != np.uint8:
            page_image = (page_image * 255).astype(np.uint8)
        
        results = reader.readtext(page_image)
        
        print("\n=== OCR Results ===")
        print("Format: [Bounding Box] Confidence: Text")
        print("-" * 50)
        
        for (bbox, text, confidence) in results:
            print(f"[{bbox[0][0]:.0f},{bbox[0][1]:.0f}] {confidence:.3f}: {text}")
        
        print("\n=== Text Only ===")
        for (bbox, text, confidence) in results:
            if confidence > 0.5:  # Filter by confidence
                print(text)
                
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have installed EasyOCR: pip install easyocr")

if __name__ == "__main__":
    main() 