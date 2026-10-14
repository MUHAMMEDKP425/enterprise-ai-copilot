from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

from backend.app.rag_service import ask_rag
from backend.app.document_service import process_pdf
from backend.app.document_management import (
    list_documents,
    delete_document,
)

app = FastAPI(title="Enterprise AI Copilot")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    document_name: str | None = None
    chat_history: list[ChatMessage] = Field(default_factory=list)


@app.get("/")
def home():
    return {"message": "Enterprise AI Copilot is running!"}


@app.post("/chat")
def chat(request: ChatRequest):
    # Only accept user/assistant messages as conversation context.
    history = [
        {"role": item.role, "content": item.content}
        for item in request.chat_history
        if item.role in ("user", "assistant")
    ]

    result = ask_rag(
        request.message,
        document_name=request.document_name,
        chat_history=history,
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"],
    }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    pdf_bytes = await file.read()

    if not pdf_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty.",
        )

    try:
        result = process_pdf(
            pdf_bytes=pdf_bytes,
            filename=file.filename,
        )
        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        print(f"PDF processing error: {error}")
        raise HTTPException(
            status_code=500,
            detail="PDF processing failed. Check the server terminal.",
        )

    finally:
        await file.close()


@app.get("/documents")
def get_documents():
    return {
        "documents": list_documents()
    }


@app.delete("/documents/{filename}")
def remove_document(filename: str):
    deleted = delete_document(filename)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Document '{filename}' was not found.",
        )

    return {
        "message": f"Document '{filename}' deleted successfully."
    }
