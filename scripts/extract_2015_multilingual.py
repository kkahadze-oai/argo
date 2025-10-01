from doctr.io import DocumentFile
from doctr.models import from_hub, ocr_predictor

# Load multilingual OCR model that supports Georgian
print("Loading multilingual model...")
det_model = from_hub("Felix92/doctr-torch-parseq-multilingual-v1")
model = ocr_predictor(det_arch='db_resnet50', reco_arch=det_model, pretrained=True)

# Load all pages from PDF first
print("Loading PDF...")
all_pages = DocumentFile.from_pdf("data/qarTul_megrul_lazur_svanur_inglisuri_leq.pdf")

# Select only page 14 (index 13 because it's 0-based)
if len(all_pages) > 13:
    doc = [all_pages[13]]  # Create a list with just page 14
    print(f"Processing page 14 of {len(all_pages)} pages")
else:
    print(f"PDF only has {len(all_pages)} pages, but you requested page 14")
    exit(1)

# Analyze it
print("Running OCR...")
result = model(doc)

# Print structured text line-by-line
print("\n=== OCR Results ===")
for page in result.pages:
    for block in page.blocks:
        for line in block.lines:
            print(" | ".join(word.value for word in line.words)) 