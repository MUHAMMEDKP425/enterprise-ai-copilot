from qdrant_client.models import Filter, FieldCondition, MatchValue

from backend.app.qdrant_store import qdrant


COLLECTION_NAME = "company_documents"


def list_documents():
    """List documents stored in Qdrant."""

    documents = {}
    next_offset = None

    while True:
        points, next_offset = qdrant.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            offset=next_offset,
            with_payload=True,
            with_vectors=False,
        )

        for point in points:
            payload = point.payload or {}
            filename = payload.get("source", "Unknown document")

            if filename not in documents:
                documents[filename] = {
                    "filename": filename,
                    "chunks": 0,
                    "pages": set(),
                }

            documents[filename]["chunks"] += 1

            page = payload.get("page")
            if page is not None:
                documents[filename]["pages"].add(page)

        if next_offset is None:
            break

    return [
        {
            "filename": document["filename"],
            "chunks": document["chunks"],
            "pages": sorted(document["pages"]),
        }
        for document in documents.values()
    ]


def delete_document(filename: str):
    """Delete all chunks belonging to one document."""

    documents = list_documents()

    document_exists = any(
        document["filename"] == filename
        for document in documents
    )

    if not document_exists:
        return False

    document_filter = Filter(
        must=[
            FieldCondition(
                key="source",
                match=MatchValue(value=filename),
            )
        ]
    )

    qdrant.delete(
        collection_name=COLLECTION_NAME,
        points_selector=document_filter,
        wait=True,
    )

    return True