import streamlit as st
import os
import glob
from tqdm import tqdm
import pandas as pd
from nyctibius import Harmonizer
from langchain_groq.chat_models import ChatGroq
from pandasai import Agent
from streamlit.components.v1 import html

def initialize_session_state():
    if 'Data_Bases' not in st.session_state:
        st.session_state.Data_Bases = []
    if 'Merge_Base' not in st.session_state:
        st.session_state.Merge_Base = None
    if 'merge_cols' not in st.session_state:
        st.session_state.merge_cols = []
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'groq_key' not in st.session_state:
        st.session_state.groq_key = None
    if 'chat_df' not in st.session_state:
        st.session_state.chat_df = None
    if "source_data" not in st.session_state:
        st.session_state.source_data = None

def threshold_data(df):
    threshold = st.slider("NaN Threshold for DataBase", 0, 100, 10, step=10)
    if st.button("Apply Threshold 1", key="t"):
        return filter_columns_by_nan_threshold(df, threshold)
        
def filter_columns(df):
    columns = st.multiselect("Choose columns for Dataset ", df.columns)
    if st.button("Select Columns", key="c"):
        return df.loc[:,columns]

def mode(series):
    mode = series.mode()
    if len(mode) > 1:
        return ','.join(mode)
    else:
        return mode.iloc[0]
    
def filter_columns_by_nan_threshold(dataframe, threshold):
    nan_percentage = dataframe.isna().mean() * 100
    filtered_columns = nan_percentage[nan_percentage < threshold].index
    return dataframe[filtered_columns]

@st.cache_data
def load_covidcol_data():
    dfs = [pd.read_csv("data/Test_Censo_col_mini.csv"),pd.read_csv("data/Test_Censo_col_mini_cundinamarca.csv")]
    return [pd.concat(dfs, ignore_index=True),pd.read_csv("data/Test_Covid_col_mini.csv", low_memory=False)]
# Function to generate bot response
def get_bot_response(agent, user_input):
    user_input = user_input.lower()
    if "hello" in user_input or "hi" == user_input:
        return "Hello! How can I help you today?"
    elif "how are you" in user_input:
        return "I'm doing well, thank you for asking. How about you?"
    elif "bye" in user_input or "goodbye" in user_input:
        return "Goodbye! Have a great day!"
    elif "name" in user_input:
        return "My name is ChatBot. Nice to meet you!"
    else:
        return agent.chat(user_input)#"I'm sorry, I don't understand that. Can you please rephrase or ask something else?"


def mermaid(code: str) -> None:
    html(
        f"""
        <pre class="mermaid">
            {code}
        </pre>

        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        """,
        height= 100,
    )