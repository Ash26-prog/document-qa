# app.py
# Combined Streamlit app: Set A (Document Q&A) + Set B (Disease Awareness Chatbot UI)
# - Supports .txt, .csv, .xlsx
# - Streams responses using OpenAI client (OpenAI Python package)
#
# Usage:
# 1. Set or paste your OpenAI API key in the sidebar.
# 2. Run: streamlit run app.py
#
# Required packages:
# pip install streamlit openai pandas openpyxl python-dotenv

import streamlit as st
from openai import OpenAI
import pandas as pd
from io import BytesIO

# ---------- Page config (from Set B) ----------
st.set_page_config(page_title="📄+🩺 Doc Q&A & Disease Awareness", page_icon="💬💊", layout="wide")

# ---------- Sidebar (from Set B) ----------
with st.sidebar:
    st.header("🔑 Settings")
    openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.markdown("👉 [Get your API key here](https://platform.openai.com/account/api-keys)")
    st.divider()
    st.info("Your key is only used in this session.", icon="ℹ️")
    st.divider()
    st.write("Supported document types: `.txt`, `.csv`, `.xlsx`")

if not openai_api_key:
    st.info("Please add your OpenAI API key in the sidebar to continue.", icon="🗝️")
    st.stop()  # stop until API key provided

# Create OpenAI client (used by both flows)
client = OpenAI(api_key=openai_api_key)

# ---------- Top-level tabs ----------
tab_doc, tab_chat, tab_about = st.tabs(["📄 Document Q&A (Set A)", "🩺 Disease Chatbot (Set B)", "ℹ️ About"])

# --------------------
# Helper utilities
# --------------------
def extract_text_from_uploaded_file(uploaded_file) -> str:
    """
    Accepts a Streamlit UploadedFile and returns a text representation.
    Supports: txt, csv, xlsx
    """
    fname = uploaded_file.name.lower()
    raw = uploaded_file.read()
    # reset pointer not necessary since we consumed bytes; uploaded_file can't be read again
    if fname.endswith(".txt") or fname.endswith(".md"):
        try:
            return raw.decode("utf-8", errors="replace")
        except Exception:
            return str(raw)
    elif fname.endswith(".csv"):
        try:
            df = pd.read_csv(BytesIO(raw))
            # provide a readable text representation (first N rows)
            return df.to_csv(index=False)
        except Exception as e:
            return f"Could not parse CSV file: {e}"
    elif fname.endswith(".xlsx") or fname.endswith(".xls"):
        try:
            df = pd.read_excel(BytesIO(raw), engine="openpyxl")
            return df.to_csv(index=False)
        except Exception as e:
            return f"Could not parse Excel file: {e}"
    else:
        # fallback
        try:
            return raw.decode("utf-8", errors="replace")
        except Exception:
            return str(raw)

def trim_text_for_prompt(text: str, max_chars: int = 30000) -> str:
    """
    Trim the document text to a sensible size for prompt/streaming.
    Adjust max_chars if you intend to send larger documents.
    """
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n...[truncated]"
    return text

# --------------------
# Document Q&A Tab (Set A functionality)
# --------------------
with tab_doc:
    # Title & description (from Set A)
    st.title("📄 Document question answering")
    st.write(
        "Upload a document (.txt, .csv, .xlsx) and ask a question about it – GPT will answer! "
        "To use this app, provide an OpenAI API key in the sidebar."
    )

    # File uploader: Accept only .txt, .csv, .xlsx
    uploaded_file = st.file_uploader(
        "Upload a document (.txt, .csv, .xlsx)",
        type=("txt", "csv", "xlsx"),
        help="Supported: .txt, .csv, .xlsx"
    )

    # Show a short preview when file uploaded
    document_text = ""
    if uploaded_file is not None:
        with st.expander("Preview uploaded document"):
            # Extract text
            document_text = extract_text_from_uploaded_file(uploaded_file)
            # Show first 5000 characters to avoid UI overload
            preview = document_text[:5000]
            st.code(preview if preview else "(empty file or unreadable format)")
            if len(document_text) > 5000:
                st.caption("Preview truncated. Full text will be used (up to the internal trim limit) when answering.")

    # Question box (like Set A)
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    # Document Q&A action
    if uploaded_file and question:
        # Prepare the document text (trim to safe size)
        full_doc_text = trim_text_for_prompt(document_text, max_chars=30000)

        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions about an uploaded document."},
            {"role": "user", "content": f"Here's a document:\n\n{full_doc_text}\n\n---\n\n{question}"},
        ]

        st.markdown("**Answer (streaming):**")
        # stream and display using st.write_stream (keeps parity with original Set A)
        try:
            stream = client.chat.completions.create(
                model="gpt-5-nano-2025-08-07",
                messages=messages,
                stream=True,
            )
            # st.write_stream returns the assembled response in some SDKs; we'll call it and capture
            response = st.write_stream(stream)
            # Optionally show full response below
            if response:
                st.success("Answer completed.")
        except Exception as e:
            st.error(f"Error while generating answer: {e}")

# --------------------
# Disease Chatbot Tab (Set B content)
# --------------------
with tab_chat:
    st.title("🩺 Disease Awareness Chatbot")
    st.write("Ask me about diseases, symptoms, and preventive care. ⚕️")

    # Initialize session messages (from Set B)
    if "disease_messages" not in st.session_state:
        st.session_state.disease_messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful medical awareness assistant. "
                    "Provide reliable health information in simple language. "
                    "Always remind users to consult a doctor for actual medical advice."
                )
            }
        ]

    # Render chat history
    for msg in st.session_state.disease_messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        elif msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])

    # Chat input (from Set B)
    if prompt := st.chat_input("Ask about a disease, symptom, or prevention tip..."):
        st.session_state.disease_messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Call OpenAI streaming completion and show assistant message streaming
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 🤔"):
                try:
                    stream = client.chat.completions.create(
                        model="gpt-5-nano-2025-08-07",
                        messages=st.session_state.disease_messages,
                        stream=True,
                    )
                    # st.write_stream in chat context returns assembled text in some SDKs.
                    response_text = st.write_stream(stream)
                except Exception as e:
                    response_text = f"Error while generating response: {e}"
                    st.error(response_text)

        # Append assistant response to session
        st.session_state.disease_messages.append({"role": "assistant", "content": response_text})

# --------------------
# About Tab (from Set B)
# --------------------
with tab_about:
    st.title("ℹ️ About This App")
    st.write(
        """
        ### What this app does
        This combined app has two main features:
        1. **Document Q&A** — Upload a `.txt`, `.csv`, or `.xlsx` file and ask questions about its content (preserves Set A behavior).
        2. **Disease Awareness Chatbot** — A friendly chat interface that answers health-related questions and provides prevention tips (from Set B).

        🔹 **Disclaimer**  
        This app provides general information and is **not a substitute for professional medical advice**. Always consult a qualified healthcare provider for diagnosis and treatment.

        🔹 **Technical notes**  
        - The app uses the OpenAI Python client and streams responses where supported.  
        - Uploaded CSV / XLSX files are converted to CSV text for the LLM to read. For very large files, text is truncated to a safe size before sending to the model.

        💡 Built with [Streamlit](https://streamlit.io) and OpenAI API.
        """
    )

# End of file
