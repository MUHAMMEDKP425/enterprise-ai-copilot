import pymupdf
import re

pdf_path = "data/documents/Enterprise_AI_Copilot_Test_Company_Policy.pdf"

document = pymupdf.open(pdf_path)

full_text = ""

for page in document:
    full_text += page.get_text()

document.close()


# Split when a new numbered section starts
chunks = re.split(r"\n(?=\d+\.\s)", full_text)

# Remove empty chunks
chunks = [chunk.strip() for chunk in chunks if chunk.strip()]


for number, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {number} ---")
    print(chunk)