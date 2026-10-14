import re

import pymupdf
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance,
)

# 1. Read the PDF
pdf_path = "data/documents/Enterprise_AI_Copilot_Test_Company_Policy.pdf"

document = pymupdf.open(pdf_path)

pages = []

for page_number, page in enumerate(document, start=1):
    page_text = page.get_text()

    pages.append({
        "page": page_number,
        "text": page_text,
    })

document.close()

# 2. Split each page into sections and preserve page numbers
chunks = []

for page in pages:
    page_number = page["page"]
    page_text = page["text"]

    page_chunks = re.split(
        r"\n(?=\d+\.\s)",
        page_text,
    )

    page_chunks = [
        chunk.strip()
        for chunk in page_chunks
        if chunk.strip()
    ]

    for chunk in page_chunks:
        chunks.append({
            "text": chunk,
            "page": page_number,
        })

if not chunks:
    raise ValueError("No text chunks were extracted from the PDF.")

print(f"Extracted {len(chunks)} chunks.")

# 3. Create embeddings from chunk text
model = SentenceTransformer("all-MiniLM-L6-v2")

chunk_texts = [chunk["text"] for chunk in chunks]
embeddings = model.encode(chunk_texts)

# 4. Connect to local Qdrant
client = QdrantClient(path="qdrant_data")

try:
    # 5. Replace the old collection
    if client.collection_exists("company_documents"):
        client.delete_collection("company_documents")

    # 6. Create a new collection
    client.create_collection(
        collection_name="company_documents",
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
    )

    # 7. Prepare chunks with page metadata
    points = []

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        point = PointStruct(
            id=index,
            vector=embedding.tolist(),
            payload={
                "text": chunk["text"],
                "source": "Enterprise_AI_Copilot_Test_Company_Policy.pdf",
                "page": chunk["page"],
                "section": chunk["text"].split("\n")[0],
            },
        )

        points.append(point)

    # 8. Store the chunks in Qdrant
    client.upsert(
        collection_name="company_documents",
        points=points,
    )

    print(f"Successfully stored {len(points)} chunks in Qdrant!")

    for index, chunk in enumerate(chunks):
        print(f"\nChunk {index}")
        print(f"Page: {chunk['page']}")
        print(f"Text: {chunk['text'][:100]}...")

finally:
    client.close()