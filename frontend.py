import requests
import streamlit as st

from backend.app.chat_history import (
    create_conversation,
    delete_conversation,
    get_messages,
    list_conversations,
    save_message,
)

# =========================================================
# 1. CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Enterprise AI Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 2. SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "confirm_delete_document" not in st.session_state:
    st.session_state.confirm_delete_document = None

if "confirm_delete_chat" not in st.session_state:
    st.session_state.confirm_delete_chat = None

if "selected_document_name" not in st.session_state:
    st.session_state.selected_document_name = None

if "active_chat_scope" not in st.session_state:
    st.session_state.active_chat_scope = None


# =========================================================
# 3. HELPER FUNCTIONS
# =========================================================

def get_documents():
    """Retrieve the current document list from FastAPI."""
    response = requests.get(f"{API_URL}/documents", timeout=30)
    response.raise_for_status()
    return response.json().get("documents", [])


def upload_document(uploaded_file):
    """Upload a PDF to the backend."""
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "application/pdf",
        )
    }
    response = requests.post(
        f"{API_URL}/upload",
        files=files,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def delete_document(filename):
    """Delete a document's indexed content from Qdrant."""
    response = requests.delete(
        f"{API_URL}/documents/{filename}",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def ask_question(question, document_name=None, chat_history=None):
    """Send the question, document filter, and previous messages to FastAPI."""
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "message": question,
            "document_name": document_name,
            "chat_history": chat_history or [],
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def display_sources(sources):
    """Display source references for an answer."""
    if not sources:
        return

    with st.expander("📚 View sources", expanded=False):
        for index, source in enumerate(sources, start=1):
            st.markdown(f"**Source {index}**")
            st.write(f"📄 Document: {source.get('document', 'Unknown')}")
            st.write(f"📌 Section: {source.get('section', 'Unknown')}")
            st.write(f"📃 Page: {source.get('page', 'Unknown')}")

            score = source.get("similarity_score")
            if score is not None:
                st.write(f"🎯 Similarity score: {score}")

            if index < len(sources):
                st.divider()


def start_new_conversation():
    """Start a fresh unsaved conversation."""
    st.session_state.conversation_id = None
    st.session_state.messages = []
    st.session_state.active_chat_scope = None
    st.session_state.confirm_delete_chat = None


def load_conversation(conversation_id):
    """Load a saved conversation and its stored document scope."""
    conversations = list_conversations()
    selected = next(
        (item for item in conversations if item["id"] == conversation_id),
        None,
    )
    if selected is None:
        start_new_conversation()
        return

    st.session_state.conversation_id = conversation_id
    st.session_state.messages = get_messages(conversation_id)
    st.session_state.active_chat_scope = selected.get("document_name")
    st.session_state.selected_document_name = selected.get("document_name")


def get_conversation_title(question):
    """Use the first question as a short conversation title."""
    title = " ".join(question.strip().split())
    if len(title) > 45:
        title = title[:42].rstrip() + "..."
    return title or "New conversation"


# =========================================================
# 4. CUSTOM STYLING
# =========================================================

st.markdown(
    """
    <style>
        :root {
            --copilot-accent: #6ee7d8;
            --copilot-accent-strong: #2dd4bf;
            --copilot-panel: #151c2b;
            --copilot-border: rgba(148, 163, 184, 0.20);
        }
        .stApp {
            background:
                radial-gradient(ellipse at 80% 0%, rgba(45, 212, 191, .09), transparent 34%),
                linear-gradient(145deg, #0b1120 0%, #101827 48%, #0b1220 100%);
        }
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
            max-width: 1250px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #141b2a 0%, #101725 100%);
            border-right: 1px solid var(--copilot-border);
        }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 { letter-spacing: -0.025em; }
        .app-hero {
            position: relative;
            overflow: hidden;
            padding: 1.7rem 1.8rem 1.45rem;
            border: 1px solid rgba(110, 231, 216, .22);
            border-radius: 22px;
            margin-bottom: 1.25rem;
            background: linear-gradient(120deg, rgba(24, 38, 56, .96), rgba(18, 32, 47, .82));
            box-shadow: 0 18px 55px rgba(0, 0, 0, .18);
            animation: fadeSlideIn 450ms ease-out both;
        }
        .app-hero:after {
            content: "";
            position: absolute;
            width: 210px; height: 210px;
            right: -75px; top: -105px;
            border: 1px solid rgba(110, 231, 216, .18);
            border-radius: 50%;
            box-shadow: 0 0 0 24px rgba(110, 231, 216, .035), 0 0 0 48px rgba(110, 231, 216, .025);
            pointer-events: none;
        }
        .app-hero h1 { letter-spacing: -.045em; font-size: clamp(1.8rem, 3vw, 2.6rem); }
        .app-eyebrow {
            color: var(--copilot-accent);
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .16em;
            text-transform: uppercase;
            margin-bottom: .55rem;
        }
        .app-subtitle { color: #a9b7c9; font-size: 1rem; margin: .55rem 0 0; }
        .feature-card {
            padding: 1.1rem 1.2rem;
            border: 1px solid var(--copilot-border);
            border-radius: 16px;
            margin-bottom: .75rem;
            background: rgba(22, 32, 48, .76);
            box-shadow: 0 8px 24px rgba(0, 0, 0, .08);
            animation: fadeSlideIn 450ms ease-out both;
            transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
        }
        .feature-card:hover {
            transform: translateY(-3px);
            border-color: rgba(110, 231, 216, .55);
            box-shadow: 0 12px 28px rgba(0, 0, 0, .18);
        }
        div[data-testid="stChatMessage"] {
            padding: 1rem 1.1rem;
            border: 1px solid rgba(148, 163, 184, .12);
            border-radius: 18px;
            background: rgba(21, 30, 45, .58);
            animation: messageAppear 260ms ease-out both;
        }
        div[data-testid="stChatInput"] {
            border: 1px solid rgba(110, 231, 216, .32);
            border-radius: 18px;
            box-shadow: 0 8px 28px rgba(0, 0, 0, .16);
        }
        div[data-testid="stButton"] button {
            border-radius: 12px;
            border-color: rgba(148, 163, 184, .22);
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
        }
        div[data-testid="stButton"] button:hover {
            transform: translateY(-1px);
            border-color: rgba(110, 231, 216, .6);
            box-shadow: 0 5px 16px rgba(0, 0, 0, .15);
        }
        div[data-testid="stFileUploader"] section {
            border: 1px dashed rgba(110, 231, 216, .35);
            border-radius: 14px;
        }
        [data-testid="stExpander"] {
            border: 1px solid var(--copilot-border);
            border-radius: 14px;
            overflow: hidden;
        }
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stTextInput"] > div > div {
            border-radius: 11px;
        }
        hr { border-color: rgba(148, 163, 184, .16); }
        @keyframes fadeSlideIn {
            from { opacity: 0; transform: translateY(9px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes messageAppear {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 5. SIDEBAR
# =========================================================

with st.sidebar:
    st.title("🤖 AI Copilot")
    st.caption("Enterprise Knowledge Assistant")
    st.divider()

    # -------------------- CHAT HISTORY --------------------
    st.header("💬 Conversations")

    if st.button("➕ New Conversation", use_container_width=True):
        start_new_conversation()
        st.rerun()

    try:
        saved_conversations = list_conversations()
    except Exception as error:
        saved_conversations = []
        st.error(f"Could not load saved conversations: {error}")

    if saved_conversations:
        conversation_labels = {
            item["id"]: (
                f"{item['title']}  ·  {item['updated_at']}"
            )
            for item in saved_conversations
        }
        conversation_ids = [item["id"] for item in saved_conversations]

        current_id = st.session_state.conversation_id
        selected_index = (
            conversation_ids.index(current_id)
            if current_id in conversation_ids
            else None
        )

        selected_chat_id = st.selectbox(
            "Saved conversations",
            options=conversation_ids,
            index=selected_index,
            format_func=lambda chat_id: conversation_labels.get(
                chat_id, f"Conversation {chat_id}"
            ),
            placeholder="Choose a saved conversation",
            key="saved_conversation_selector",
        )

        if (
            selected_chat_id is not None
            and selected_chat_id != st.session_state.conversation_id
        ):
            load_conversation(selected_chat_id)
            st.rerun()

        if st.session_state.conversation_id in conversation_ids:
            if st.button(
                "🗑️ Delete Current Conversation",
                use_container_width=True,
            ):
                st.session_state.confirm_delete_chat = (
                    st.session_state.conversation_id
                )

        if st.session_state.confirm_delete_chat is not None:
            st.warning("Delete this conversation and all its messages?")
            confirm_col, cancel_col = st.columns(2)

            with confirm_col:
                if st.button("Confirm", key="confirm_chat_delete", type="primary"):
                    try:
                        delete_conversation(
                            st.session_state.confirm_delete_chat
                        )
                        start_new_conversation()
                        st.rerun()
                    except Exception as error:
                        st.error(f"Could not delete conversation: {error}")

            with cancel_col:
                if st.button("Cancel", key="cancel_chat_delete"):
                    st.session_state.confirm_delete_chat = None
                    st.rerun()
    else:
        st.caption("Your saved conversations will appear here.")

    st.divider()

    # -------------------- PDF UPLOAD --------------------
    st.header("📄 Document Management")
    st.subheader("Upload a PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        help="Upload a text-based PDF to make it searchable.",
    )

    if st.button(
        "⬆️ Upload Document",
        use_container_width=True,
        type="primary",
    ):
        if uploaded_file is None:
            st.warning("Please select a PDF first.")
        else:
            try:
                with st.spinner("Processing and indexing PDF..."):
                    upload_result = upload_document(uploaded_file)

                st.success("PDF uploaded successfully!")
                st.write(
                    f"**File:** "
                    f"{upload_result.get('filename', uploaded_file.name)}"
                )
                st.write(
                    f"**Pages:** {upload_result.get('pages_extracted', 'N/A')}"
                )
                st.write(
                    f"**Chunks:** {upload_result.get('chunks_stored', 'N/A')}"
                )
                st.rerun()
            except requests.RequestException as error:
                st.error(f"Upload failed: {error}")
                if getattr(error, "response", None) is not None:
                    st.error(error.response.text)

    st.divider()

    # -------------------- DOCUMENT LIBRARY --------------------
    st.subheader("📚 Your Documents")

    if st.button("🔄 Refresh Documents", use_container_width=True):
        st.rerun()

    documents = []
    documents_available = True

    try:
        documents = get_documents()
        if not documents:
            st.info("No documents uploaded yet.")
        else:
            st.caption(f"{len(documents)} document entries")
            for document in documents:
                filename = document.get("filename", "Unknown document")

                with st.expander(f"📄 {filename}"):
                    st.write(f"**Pages:** {document.get('pages', 'N/A')}")
                    st.write(f"**Chunks:** {document.get('chunks', 'N/A')}")

                    if st.button(
                        "🗑️ Delete Document",
                        key=f"delete_document_{filename}",
                        use_container_width=True,
                    ):
                        st.session_state.confirm_delete_document = filename

                    if st.session_state.confirm_delete_document == filename:
                        st.warning(
                            "This removes the indexed document from Qdrant. "
                            "It does not delete the original PDF from your computer."
                        )
                        confirm_col, cancel_col = st.columns(2)

                        with confirm_col:
                            if st.button(
                                "Confirm",
                                key=f"confirm_document_{filename}",
                                type="primary",
                            ):
                                try:
                                    delete_document(filename)
                                    st.session_state.confirm_delete_document = None
                                    st.success("Document deleted.")
                                    st.rerun()
                                except requests.RequestException as error:
                                    st.error(f"Delete failed: {error}")

                        with cancel_col:
                            if st.button(
                                "Cancel",
                                key=f"cancel_document_{filename}",
                            ):
                                st.session_state.confirm_delete_document = None
                                st.rerun()

    except requests.RequestException:
        documents_available = False
        st.warning(
            "Cannot connect to the backend. "
            "Start the FastAPI server to manage documents."
        )

    st.divider()

    # -------------------- DOCUMENT SEARCH SCOPE --------------------
    st.subheader("🔎 Search Scope")

    document_names = sorted(
        {
            document["filename"]
            for document in documents
            if document.get("filename")
        }
    )
    search_options = ["All documents"] + document_names

    # Restore a saved conversation's scope where possible.
    saved_scope = st.session_state.active_chat_scope
    default_scope = (
        saved_scope
        if saved_scope in document_names
        else "All documents"
    )

    current_scope_option = (
        default_scope
        if default_scope in search_options
        else "All documents"
    )

    selected_document = st.selectbox(
        "Search in",
        options=search_options,
        index=search_options.index(current_scope_option),
        help=(
            "Choose All documents to search the entire knowledge base, "
            "or select one PDF to search only that document."
        ),
        key="document_scope_selector",
    )

    selected_document_name = (
        None if selected_document == "All documents" else selected_document
    )

    # New chats use the currently selected scope. Existing chats keep their
    # stored scope until the user changes it.
    if st.session_state.conversation_id is None:
        st.session_state.active_chat_scope = selected_document_name
    elif selected_document_name != st.session_state.active_chat_scope:
        st.session_state.active_chat_scope = selected_document_name

    st.caption("The selected scope is saved with each conversation.")

    st.divider()

    if st.button("🧹 Clear Current Chat", use_container_width=True):
        start_new_conversation()
        st.rerun()

    st.caption("Powered by FastAPI, Qdrant, SQLite and OpenRouter")


# =========================================================
# 6. MAIN CHAT INTERFACE
# =========================================================

st.markdown(
    """
    <div class="app-hero">
        <div class="app-eyebrow">Your private knowledge workspace</div>
        <h1 style="margin:0 0 0.4rem 0;">Enterprise AI Copilot</h1>
        <p class="app-subtitle">
            Ask questions, explore your documents, and get answers with sources.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

scope_label = (
    selected_document
    if selected_document
    else "All documents"
)
st.info(f"🔎 Current search scope: **{scope_label}**")

# =========================================================
# 7. WELCOME SCREEN
# =========================================================

if not st.session_state.messages:
    st.markdown("### 👋 How can I help you?")

    st.markdown(
        """
        <div class="feature-card">
            <strong>📚 Search your knowledge base</strong><br>
            Ask questions about your uploaded PDFs.
        </div>
        <div class="feature-card">
            <strong>🔎 Search specific documents</strong><br>
            Choose one PDF or search all documents.
        </div>
        <div class="feature-card">
            <strong>💾 Saved conversations</strong><br>
            Reopen previous chats from the sidebar.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 💡 Try asking")
    st.caption("Choose a question to explore your uploaded documents.")

    example_questions = [
        "What are the company's working hours?",
        "How many days per week is remote work allowed?",
        "How far in advance should I request leave?",
    ]

    cols = st.columns(3)
    for index, example in enumerate(example_questions):
        with cols[index]:
            if st.button(
                f"💬 {example}",
                key=f"example_{index}",
                use_container_width=True,
                help="Click to ask this question",
            ):
                st.session_state.pending_question = example
                st.rerun()

# =========================================================
# 8. DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            display_sources(message.get("sources", []))

# =========================================================
# 9. CHAT INPUT
# =========================================================

question = st.chat_input("Ask a question about your documents...")

if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None

# =========================================================
# 10. PROCESS AND SAVE QUESTION
# =========================================================

if question:
    question = question.strip()

    if question:
        scope_for_question = selected_document_name

        # Create a saved conversation when the first question is sent.
        if st.session_state.conversation_id is None:
            try:
                conversation_id = create_conversation(
                    title=get_conversation_title(question),
                    document_name=scope_for_question,
                )
                st.session_state.conversation_id = conversation_id
                st.session_state.active_chat_scope = scope_for_question
            except Exception as error:
                st.error(f"Could not create a saved conversation: {error}")
                st.stop()

        conversation_id = st.session_state.conversation_id

        # Persist the user message before calling the AI.
        try:
            save_message(
                conversation_id=conversation_id,
                role="user",
                content=question,
                sources=[],
            )
        except Exception as error:
            st.error(f"Could not save your message: {error}")
            st.stop()

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
                "search_scope": scope_label,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)
            st.caption(f"Search scope: {scope_label}")

        with st.chat_message("assistant"):
            try:
                with st.spinner(
                    "Searching documents and generating an answer..."
                ):
                    # Send earlier turns only; the current question is not
                    # included in chat_history because it is sent separately.
                    previous_history = [
                        {
                            "role": item["role"],
                            "content": item["content"],
                        }
                        for item in st.session_state.messages[:-1]
                        if item.get("role") in ("user", "assistant")
                    ][-6:]

                    result = ask_question(
                        question,
                        document_name=scope_for_question,
                        chat_history=previous_history,
                    )

                answer = result.get(
                    "answer",
                    "No answer was returned by the backend.",
                )
                sources = result.get("sources", [])

                st.markdown(answer)
                display_sources(sources)

                save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=answer,
                    sources=sources,
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except requests.RequestException as error:
                error_message = (
                    "I couldn't retrieve an answer because the backend "
                    "request failed. Check that FastAPI is running."
                )
                st.error(error_message)

                if getattr(error, "response", None) is not None:
                    st.caption(error.response.text)

                try:
                    save_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=error_message,
                        sources=[],
                    )
                except Exception:
                    pass

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                        "sources": [],
                    }
                )

            except Exception as error:
                error_message = (
                    "An unexpected error occurred while processing "
                    "your question."
                )
                st.error(f"{error_message} Details: {error}")

                try:
                    save_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=error_message,
                        sources=[],
                    )
                except Exception:
                    pass

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                        "sources": [],
                    }
                )

        # Refresh sidebar labels/order after saving messages.
        st.rerun()
