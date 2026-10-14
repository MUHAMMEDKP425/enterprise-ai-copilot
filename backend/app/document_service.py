import re
import uuid

import pymupdf

from sentence_transformers import SentenceTransformer
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct

from backend.app.qdrant_store import qdrant


# 1. Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def process_pdf(pdf_bytes: bytes, filename: str):
    """
    Extract PDF text, split it into chunks, create embeddings,
    and replace existing indexed content for the same filename.
    """

    # 2. Extract text page by page
    document = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf",
    )

    pages = []

    try:
        for page_number, page in enumerate(document, start=1):
            pages.append({
                "page": page_number,
                "text": page.get_text(),
            })
    finally:
        document.close()

    # 3. Split extracted text into smaller chunks
    chunks = []

    for page in pages:
        page_number = page["page"]
        page_text = page["text"].strip()

        if not page_text:
            continue

        # Split on blank lines
        paragraphs = re.split(r"\n\s*\n", page_text)

        current_chunk = ""
        max_chunk_length = 700

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if not paragraph:
                continue

            if (
                current_chunk
                and len(current_chunk) + len(paragraph) + 1
                > max_chunk_length
            ):
                chunks.append({
                    "text": current_chunk.strip(),
                    "page": page_number,
                })
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n" + paragraph
                else:
                    current_chunk = paragraph

            # Split unusually long paragraphs
            while len(current_chunk) > max_chunk_length:
                split_at = current_chunk.rfind(
                    " ",
                    0,
                    max_chunk_length,
                )

                if split_at <= 0:
                    split_at = max_chunk_length

                chunks.append({
                    "text": current_chunk[:split_at].strip(),
                    "page": page_number,
                })

                current_chunk = current_chunk[split_at:].strip()

        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "page": page_number,
            })

    # 4. Validate extracted content before modifying Qdrant
    if not chunks:
        raise ValueError(
            "No readable text was found in the PDF."
        )

    # 5. Create embeddings
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedding_model.encode(texts)

    # 6. Check the Qdrant collection
    collection_name = "company_documents"

    if not qdrant.collection_exists(collection_name):
        raise RuntimeError(
            "Qdrant collection is missing. "
            "Run store_embeddings.py first."
        )

    # 7. Remove previously indexed chunks with this filename
    # This happens only after the new PDF has been successfully parsed
    # and its embeddings have been created.
    qdrant.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="source",
                    match=MatchValue(value=filename),
                )
            ]
        ),
        wait=True,
    )

    # 8. Store the new chunks
    points = []

    for chunk, embedding in zip(chunks, embeddings):
        first_line = chunk["text"].split("\n")[0].strip()

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={
                    "text": chunk["text"],
                    "source": filename,
                    "page": chunk["page"],
                    "section": first_line,
                },
            )
        )

    qdrant.upsert(
        collection_name=collection_name,
        points=points,
        wait=True,
    )

    # 9. Return processing information
    return {
        "filename": filename,
        "pages_extracted": len(pages),
        "chunks_stored": len(chunks),
        "message": (
            "PDF processed successfully. "
            "Existing indexed content for this filename was replaced."
        ),
    }