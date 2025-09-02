import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from utils import initialize_session_state, load_covidcol_data, generate_column_descriptions
from instructions import INSTRUCTIONS
from langchain_groq import ChatGroq

def dictionary_standarization(df):
    """

    """

# Main script
st.set_page_config(page_title="Dictionary Standardization", page_icon="📖")

#with st.expander("ℹ️ Instructions", expanded=False):
#    st.markdown(INSTRUCTIONS["data_loading"])

initialize_session_state()
if 'state' not in st.session_state:
    st.session_state.state = "Select Source"

states = ["Upload Dicctionary", "Load Data"]

st.title("Dictionary Standardization 📖")
st.subheader(f"Data Base: {len(st.session_state.Data_Bases)+1} → Select Data Source")

st.session_state.source_data = st.selectbox("Choose data source", ["Select an Option","Internet (URL)", "Local file", "Col case: Census & Covid19", "Health Data", "Test"])

if st.session_state.state == "Select Source":
    if st.button("Load Data"):
        st.session_state.state = "Load Data"
        
if st.session_state.state == "Load Data":
    source = st.session_state.source_data

    data = None
    #harmonizer = Harmonizer()
    if source == "Internet (URL)":
        st.subheader("Enter URLs for datasets")
        col1, col2 = st.columns(2)
        with col1:
            url_1 = st.text_area("Enter URL for Dataset:", height=10, value="https://microdatos.dane.gov.co/index.php/catalog/663", key="u1")
            extensions_1 = st.multiselect("Choose data source", ['.csv', '.xls', '.xlsx', ".txt", ".sav", ".zip"], default=[".csv",".zip"], key="exts")
        with col2:
            key_words_1 = st.text_area("Enter relevant keywords (separated by commas ',')", height=10, value=None, key="kw1")
            depth_1 = st.number_input('Enter a number', min_value=0, max_value=10, value=1, step=1)
        if st.button("Confirm Downloading info"):
            from socio4health import Extractor
            import pandas as pd


            def extract_data():
                extractor = Extractor(
                    input_path=url_1,
                    down_ext=extensions_1,
                    sep=';',
                    output_path="./data",
                    depth=depth_1,
                    key_words=key_words_1.split(",") if key_words_1 else None
                )
                return extractor.extract()


            extract_data()
    elif source == "Local file":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file, low_memory=False)
    elif source == "Col case: Census & Covid19":
        st.subheader("Subset: Colombian Demographic & Health Data")
        st.session_state.Data_Bases = load_covidcol_data()
    elif source == "Health Data":
        st.subheader("Data to stack an variable tracking")
        st.session_state.Data_Bases = [
            pd.read_csv("data/health_data_2018.csv", low_memory=False),
            pd.read_csv("data/health_data_2020.csv", low_memory=False),
            pd.read_csv("data/health_data_2021.csv", low_memory=False),
            pd.read_csv("data/health_data_2022.csv", low_memory=False),
            pd.read_csv("data/health_data_2023.csv", low_memory=False)
        ]
    elif source == "Test":
        data = pd.read_csv("data/Sample_Data.csv", low_memory=False)
    
    if isinstance(data, pd.DataFrame):
        st.subheader("📊 Data Preview")
        st.session_state.Data_Bases.append(data)
        st.write(st.session_state.Data_Bases[-1].head())
        st.success("Data loaded successfully!")
        
        # Perform EDA on the loaded data
        perform_eda(data)
        
        if st.button("Add new DataBase"):
            pass
    elif st.session_state.Data_Bases:
        for i, df in enumerate(st.session_state.Data_Bases):
            st.subheader(f"Database {i+1}")
            perform_eda(df)

st.write(f"Total databases loaded: {len(st.session_state.Data_Bases)}")