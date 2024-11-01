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

def load_data(source:str):
    data = None
    harmonizer = Harmonizer()

    if source == "url":
        st.subheader("Enter URLs for datasets")
        col1, col2 = st.columns(2)
        with col1:
            url_1 = st.text_area("Enter URL for Dataset:", height=10,value="https://microdatos.dane.gov.co/index.php/catalog/663",key="u1")
            extensions_1 = st.multiselect("Choose data source", ['.csv', '.xls', '.xlsx', ".txt", ".sav", ".zip"], default=[".csv",".zip"], key="exts")
        with col2:
            key_words_1 = st.text_area("Enter relevant keywords (separated by commas ',')", height=10,value=None,key="kw1")
            depth_1 = st.number_input('Enter a number', min_value=0, max_value=10, value=1, step=1)
            if st.button("Confirm Downloading info"):
                list_datainfo = harmonizer.extract(url=url_1, depth=depth_1, down_ext=extensions_1, key_words=key_words_1)
                harmonizer = Harmonizer(list_datainfo)
                data = harmonizer.transform()[0].data
                st.write("XD")
    elif source == "local":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file, low_memory=False)
    elif source == "Col case: Covid19 Data":
        st.subheader("Example Dataset 1")
        data = load_covidcol_data()
    elif source == "Col case: Col People Census Data":
        st.subheader("Example Dataset 2")
        data = load_percol_data()
    else:
        data = pd.read_csv("Sample_Data.csv", low_memory=False)
    st.write(data.head())
    return data

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
    return pd.read_csv("Casos_positivos_de_COVID-19_en_Colombia._20240519_datosabiertos.csv", low_memory=False)
@st.cache_data
def load_percol_data():
    file_pattern = os.path.join("data/input",'CNPV2018_5PER_A2_*')
    filtered_files = glob.glob(file_pattern)
    dfs = []
    for file in tqdm(filtered_files):
        df = pd.read_csv(file).loc[:, ["U_DPTO", "U_MPIO", "P_SEXO", "P_EDADR", "P_ENFERMO", "PA_LO_ATENDIERON", "PA1_CALIDAD_SERV", "P_TRABAJO"]]
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)
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