"""
Google Cloud Vision API OCR for Georgian text
Requires: pip install google-cloud-vision
And setting up Google Cloud credentials
"""

import io
from google.cloud import vision
from doctr.io import DocumentFile
import numpy as np
from PIL import Image

def ocr_with_google_vision(image_array, language_hints=['ka']):
    """
    Perform OCR using Google Cloud Vision API
    
    Args:
        image_array: numpy array of the image
        language_hints: list of language codes (ka = Georgian)
    """
    # Initialize the client
    client = vision.ImageAnnotatorClient()
    
    # Convert numpy array to PIL Image and then to bytes
    image_pil = Image.fromarray(image_array)
    img_byte_arr = io.BytesIO()
    image_pil.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Create Vision API image object
    image = vision.Image(content=img_byte_arr)
    
    # Configure image context with language hints
    image_context = vision.ImageContext(language_hints=language_hints)
    
    # Perform text detection
    response = client.document_text_detection(image=image, image_context=image_context)
    
    if response.error.message:
        raise Exception(f'{response.error.message}')
    
    return response

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
    
    # Perform OCR with Google Vision API
    print("Running Google Cloud Vision OCR...")
    try:
        response = ocr_with_google_vision(page_image, language_hints=['ka', 'en'])
        
        # Print full text
        print("\n=== Full Text ===")
        if response.full_text_annotation.text:
            print(response.full_text_annotation.text)
        
        # Print structured text (word by word)
        print("\n=== Structured Text ===")
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    words = []
                    for word in paragraph.words:
                        word_text = ''.join([symbol.text for symbol in word.symbols])
                        words.append(word_text)
                    if words:
                        print(" | ".join(words))
                        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have:")
        print("1. Installed google-cloud-vision: pip install google-cloud-vision")
        print("2. Set up Google Cloud credentials")
        print("3. Enabled the Vision API in your Google Cloud project")

if __name__ == "__main__":
    main() 