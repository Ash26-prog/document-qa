import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="🩺 Disease Awareness Chatbot", page_icon="💊", layout="wide")

with st.sidebar:
    st.header("🔑 Settings")
    openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.markdown("👉 [Get your API key here](https://platform.openai.com/account/api-keys)")
    st.divider()
    st.info("Your key is only used in this session.", icon="ℹ️")


tab1, tab2 = st.tabs(["💬 Chatbot", "ℹ️ About"])

with tab1:
    st.title("🩺 Disease Awareness Chatbot")
    st.write("Ask me about diseases, symptoms, and preventive care. ⚕️")

    if not openai_api_key:
        st.warning("Please enter your OpenAI API key in the sidebar to start chatting.", icon="🗝️")
    else:
        
        client = OpenAI(api_key=openai_api_key)

        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful medical awareness assistant. "
                        "Provide reliable health information in simple language. "
                        "Always remind users to consult a doctor for actual medical advice."
                    )
                }
            ]

    
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            elif msg["role"] == "assistant":
                st.chat_message("assistant").write(msg["content"])

        
        if prompt := st.chat_input("Ask about a disease, symptom, or prevention tip..."):
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            
            with st.chat_message("assistant"):
                with st.spinner("Thinking... 🤔"):
                    stream = client.chat.completions.create(
                        model="gpt-5-nano-2025-08-07",
                        messages=st.session_state.messages,
                        stream=True,
                    )
                    response = st.write_stream(stream)

            
            st.session_state.messages.append({"role": "assistant", "content": response})

with tab2:
    st.title("ℹ️ About This Chatbot")
    st.write("""
    ### 🩺 Disease Awareness Chatbot  
    This chatbot is designed to **raise awareness about common diseases, symptoms, and prevention methods**.  

    🔹 **Purpose**  
    - Educate users about general health conditions.  
    - Share prevention and lifestyle tips.  
    - Encourage healthy practices.  

    🔹 **Disclaimer**  
    This chatbot is **not a substitute for professional medical advice**.  
    Always consult a **qualified healthcare provider** for diagnosis and treatment.  

    🔹 **Target Audience**  
    - Students  
    - General public  
    - Awareness campaigns  

    💡 Built with [Streamlit](https://streamlit.io) and OpenAI API.
    """)
