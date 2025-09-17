import streamlit as st
from openai import OpenAI
import os

st.title("🩺 Disease Awareness Chatbot")
st.write(
    "Ask questions about diseases, symptoms, and preventive care — no file upload needed!",
    "Provide your OpenAI API key below to start chatting.",
)

openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    DATAFILE = "dataset.csv"  # put your dataset here
    if not os.path.exists(DATAFILE):
        st.error(f"Missing dataset file: {DATAFILE}")
        st.stop()

    with open(DATAFILE, "r", encoding="utf-8") as f:
        document = f.read()

    question = st.text_area(
        "Ask me about diseases, symptoms, and preventive care. ⚕️",
        placeholder="Can you give me a short summary?",
    )

    if question:
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question}",
            }
        ]

        stream = client.chat.completions.create(
            model="gpt-5-nano-2025-08-07",
            messages=messages,
            stream=True,
        )
        st.write_stream(stream)
