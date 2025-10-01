"""
Test Tesseract's ability to recognize Mingrelian-specific characters ჸ and ჷ
"""

import pytesseract
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_test_image_with_mingrelian_chars():
    """Create a test image with Mingrelian characters"""
    # Create a white image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a Georgian font if available, otherwise use default
    try:
        # Try to find a Georgian font (you might need to adjust the path)
        font = ImageFont.truetype("/System/Library/Fonts/Arial Unicode.ttf", 48)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        except:
            font = ImageFont.load_default()
    
    # Text with Mingrelian characters
    mingrelian_text = "ჸარი ჷოლი აბგდ"  # ჸ and ჷ with some regular Georgian
    
    # Draw the text
    draw.text((50, 50), mingrelian_text, fill='black', font=font)
    
    # Also add some context
    draw.text((50, 120), "Regular Georgian: აბგდევზ", fill='black', font=font)
    
    return img

def test_mingrelian_recognition():
    """Test different Tesseract models on Mingrelian characters"""
    
    # Create test image
    test_img = create_test_image_with_mingrelian_chars()
    test_img.save("mingrelian_test.png")
    print("Created test image: mingrelian_test.png")
    
    # Test different language configurations
    language_configs = [
        ('kat', 'Georgian'),
        ('kat_old', 'Old Georgian'),
        ('kat+eng', 'Georgian + English'),
        ('script/Georgian', 'Georgian Script'),
        ('eng', 'English (for comparison)')
    ]
    
    print("\nTesting Mingrelian character recognition:")
    print("Test text contains: ჸარი ჷოლი აბგდ")
    print("=" * 60)
    
    for lang_code, description in language_configs:
        print(f"\n{description} ({lang_code}):")
        try:
            result = pytesseract.image_to_string(test_img, lang=lang_code)
            print(f"Result: '{result.strip()}'")
            
            # Check if the special characters are recognized
            if 'ჸ' in result:
                print("✓ ჸ (U+10F8) recognized!")
            else:
                print("✗ ჸ (U+10F8) not recognized")
                
            if 'ჷ' in result:
                print("✓ ჷ (U+10F7) recognized!")
            else:
                print("✗ ჷ (U+10F7) not recognized")
                
        except Exception as e:
            print(f"Error: {e}")

def main():
    test_mingrelian_recognition()
    
    print("\n" + "=" * 60)
    print("Note: Mingrelian uses extended Georgian script with additional letters:")
    print("ჸ (U+10F8) - used in Mingrelian")
    print("ჷ (U+10F7) - used in Mingrelian") 
    print("These may not be well-supported in standard Georgian OCR models.")

if __name__ == "__main__":
    main() 