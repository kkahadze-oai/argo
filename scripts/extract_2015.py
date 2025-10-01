from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# Load OCR model
model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

# Load all pages from PDF first
all_pages = DocumentFile.from_pdf("data/qarTul_megrul_lazur_svanur_inglisuri_leq.pdf")

# Select only page 14 (index 13 because it's 0-based)
if len(all_pages) > 13:
    doc = [all_pages[13]]  # Create a list with just page 14
else:
    print(f"PDF only has {len(all_pages)} pages, but you requested page 14")
    exit(1)

# Analyze it
result = model(doc)

# Print structured text line-by-line
for page in result.pages:
    for block in page.blocks:
        for line in block.lines:
            print(" | ".join(word.value for word in line.words))
