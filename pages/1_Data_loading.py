import streamlit as st
import pandas as pd
from utils import initialize_session_state
from  utils import load_covidcol_data, load_percol_data, Harmonizer
from instructions import INSTRUCTIONS
st.set_page_config(page_title="Data Loading", page_icon="🗃️")

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown(INSTRUCTIONS["data_loading"])

initialize_session_state()
if 'state' not in st.session_state:
    st.session_state.state = "Select Source"

states = ["Select Source",
          "Load Data"]

st.title("Data Loading 🗃️")
st.subheader(f"Data Base: {len(st.session_state.Data_Bases)+1} → Select Data Source")

col_case = "Col case: Covid19 Data" if len(st.session_state.Data_Bases) == 0 else "Col case: Col People Census Data"
st.session_state.source_data = st.selectbox("Choose data source", ["url", "local", col_case, "Health Data", "Test"])

if st.session_state.state == "Select Source":
    if st.button("Load Data"):
        st.session_state.state = "Load Data"
        
if st.session_state.state == "Load Data":
    source = st.session_state.source_data

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
    elif source == "Health Data":
        st.session_state.Data_Bases = [pd.read_csv("data/health_data_2018.csv", low_memory=False), pd.read_csv("data/health_data_2020.csv", low_memory=False), 
                                       pd.read_csv("data/health_data_2021.csv", low_memory=False), pd.read_csv("data/health_data_2022.csv", low_memory=False), 
                                       pd.read_csv("data/health_data_2023.csv", low_memory=False)]
    else:
        data = pd.read_csv("data/Sample_Data.csv", low_memory=False)
    
    if isinstance(data, pd.DataFrame):
        st.session_state.Data_Bases.append(data)
        st.write(st.session_state.Data_Bases[-1].head())
        st.success("Data loaded successfully!")
        if st.button("Add new DataBase"):
            pass


st.write(f"Total databases loaded: {len(st.session_state.Data_Bases)}")



