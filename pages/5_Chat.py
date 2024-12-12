import streamlit as st
from nyctibius import BirdAgent
from utils import get_bot_response
from langchain_groq import ChatGroq
import pandas as pd
from instructions import INSTRUCTIONS
from pandasai import Agent
from utils import MyStResponseParser, generate_sample_questions
import pyperclip

st.set_page_config(page_title="Chat with Data", page_icon="💬")

st.title("Chat with your data 💬")

if "sample_questions" not in st.session_state:
    st.session_state.sample_questions = []

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown(INSTRUCTIONS["chat"])

# Groq API key input
st.sidebar.text_input(label="🗝️ Groq Key:", key="groq_key", help="Required for Chat with data.", type="password")

if not st.session_state.Data_Bases:
    st.warning("No data loaded. Please load data first.")

elif not st.session_state.groq_key:
    st.warning("No Key registered. Please register a Groq Key first 🗝️")
    st.warning("If you dont have one. Try this one: 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")

else:

    db_index = st.selectbox("Select database to Chat", range(len(st.session_state.Data_Bases)), format_func=lambda x: f"Database {x+1}")
    st.session_state.chat_df = st.session_state.Data_Bases[db_index]
    st.write(st.session_state.chat_df.head())

    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",#llama3-70b-8192 
        api_key=st.session_state.groq_key,
        max_retries=100
    )

    with st.spinner("🔄 Analyzing your data..."):
        st.session_state.sample_questions = generate_sample_questions(st.session_state.chat_df, llm)
        st.markdown("### 🤔 Sample Questions You Can Ask")
        st.markdown("""
            Below are some example questions you can ask about your dataset. 
            Click any 'Copy' button to copy the question to your clipboard!
        """)
        
        for i, qa in enumerate(st.session_state.sample_questions, 1):
            with st.expander(f"❓ Question {i}: {qa['question']}"):
                if st.button(f"📋 Copy Question", key=f"copy_q_{i}"):
                    try:
                        pyperclip.copy(qa['question'])
                        st.success("Question copied to clipboard!")
                    except Exception as e:
                        st.error(f"Failed to copy: {str(e)}")
                        # Fallback JavaScript method
                        st.markdown(
                            f"""
                            <script>
                                copyToClipboard("{qa['question']}");
                            </script>
                            """,
                            unsafe_allow_html=True
                        )
  
    agent = Agent(dfs=st.session_state.chat_df, config={"llm": llm, "response_parser": MyStResponseParser})
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": {"value":"Hello! Let’s dive into your data", "type":"string"}})
    for message in st.session_state.messages:
        if message["role"] == "assistant": 
            with st.chat_message(message["role"]):
                if message["content"]['type'] == "dataframe":
                    st.dataframe(message["content"]['value'])
                elif message["content"]['type'] == 'plot':
                    st.image(message["content"]["value"])
                else:
                    st.write(message["content"]['value'])
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("What is your question?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            response = get_bot_response(agent, prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

