import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
from tqdm import tqdm
from nyctibius import Harmonizer

# Set page configuration
st.set_page_config(page_title="Demo4Health Data Analysis", layout="wide")

# Initialize session state variables
if 'step' not in st.session_state:
    st.session_state.step = -1
if 'data_1' not in st.session_state:
    st.session_state.data_1 = None
if 'filtered_df_1' not in st.session_state:
    st.session_state.filtered_df_1 = None
if 'selected_columns_1' not in st.session_state:
    st.session_state.selected_columns_1 = None
if 'agg_functions_1' not in st.session_state:
    st.session_state.agg_functions_1 = None
if 'agg_df_1' not in st.session_state:
    st.session_state.agg_df_1 = None
if 'data_2' not in st.session_state:
    st.session_state.data_2 = None
if 'filtered_df_2' not in st.session_state:
    st.session_state.filtered_df_2 = None
if 'selected_columns_2' not in st.session_state:
    st.session_state.selected_columns_2 = None
if 'agg_functions_2' not in st.session_state:
    st.session_state.agg_functions_2 = None
if 'agg_df_2' not in st.session_state:
    st.session_state.agg_df_2 = None
if 'merged_df' not in st.session_state:
    st.session_state.merged_df = None
if 'data_source1' not in st.session_state:
    st.session_state.data_source1 = None
if 'data_source2' not in st.session_state:
    st.session_state.data_source2 = None
if 'agg_list1' not in st.session_state:
    st.session_state.agg_list1 = False
if 'col_agg1' not in st.session_state:
    st.session_state.col_agg1 = False

# Main content
st.title("Socio4Health Data Analysis")

def load_data_1():
    st.session_state.data_1 = pd.read_csv("Casos_positivos_de_COVID-19_en_Colombia._20240519_datosabiertos.csv", low_memory=False)
    st.write(st.session_state.data_1.head())
    st.session_state.step = 1

def load_data_2():
    file_pattern = os.path.join("data/input",'CNPV2018_5PER_A2_*')
    filtered_files = glob.glob(file_pattern)
    dfs = []
    for file in tqdm(filtered_files):
        df = pd.read_csv(file).loc[:, ["U_DPTO", "U_MPIO", "P_SEXO", "P_EDADR", "P_ENFERMO", "PA_LO_ATENDIERON", "PA1_CALIDAD_SERV", "P_TRABAJO"]]
        dfs.append(df)
    st.session_state.data_2 = pd.concat(dfs, ignore_index=True)
    st.write(st.session_state.data_2.head())
    st.session_state.step = 7

def filter_columns_by_nan_threshold(dataframe, threshold):
    nan_percentage = dataframe.isna().mean() * 100
    filtered_columns = nan_percentage[nan_percentage < threshold].index
    return dataframe[filtered_columns]

def apply_threshold_1():
    threshold = st.session_state.threshold_1
    st.session_state.filtered_df_1 = filter_columns_by_nan_threshold(st.session_state.data_1, threshold)

def apply_threshold_2():
    threshold = st.session_state.threshold_2
    st.session_state.filtered_df_2 = filter_columns_by_nan_threshold(st.session_state.data_2, threshold)

def select_columns_1():
    st.session_state.selected_columns_1 = st.session_state.columns_1

def select_columns_2():
    st.session_state.selected_columns_2 = st.session_state.columns_2

def select_agg_functions_1():
    st.session_state.agg_functions_1 = {col: st.session_state[f"agg_1_{col}"] for col in st.session_state.selected_columns_1}

def select_agg_functions_2():
    st.session_state.agg_functions_2 = {col: st.session_state[f"agg_2_{col}"] for col in st.session_state.selected_columns_2}

def perform_aggregation_1(column):
    st.session_state.agg_df_1 = st.session_state.filtered_df_1[st.session_state.selected_columns_1].groupby(column).agg(st.session_state.agg_functions_1).drop(column, axis=1)

def perform_aggregation_2(column):
    st.session_state.agg_df_2 = st.session_state.filtered_df_2[st.session_state.selected_columns_2].groupby(column).agg(st.session_state.agg_functions_2).drop(column, axis=1)

def merge_dataframes():
    st.session_state.merged_df = pd.merge(st.session_state.agg_df_1.drop("Código DIVIPOLA departamento", axis=1), st.session_state.agg_df_2.drop("U_DPTO", axis=1), 
                                          left_on='Código DIVIPOLA departamento', right_on='U_DPTO', how='inner')

def mode(series):
    mode = series.mode()
    if len(mode) > 1:
        return ','.join(mode)
    else:
        return mode.iloc[0]


# New initial step: Select data source
if st.session_state.step >= -1:
    st.subheader("Step 0: Select Data Source")
    st.session_state.data_source1 = st.selectbox("Choose data source", ["url", "local", "Col case"])
    if st.button("Confirm Data Source"):
        st.session_state.step = 0

if st.session_state.step >= 0:
    st.subheader("Step 1: Load Data")
    harmonizer = Harmonizer()
    if st.session_state.data_source1 == "url":
        st.subheader("Enter URLs for datasets")
        col1, col2 = st.columns(2)
        with col1:
            url_1 = st.text_area("Enter URL for Dataset:", height=10,value=None,key="u1")
            extensions_1 = st.multiselect("Choose data source", ['.csv', '.xls', '.xlsx', ".txt", ".sav", ".zip"], default=[".csv",".zip"])
        with col2:
            key_words_1 = st.text_area("Enter relevant keywords (separated by commas ',')", height=10,value=None,key="kw1")
            depth_1 = st.number_input('Enter a number', min_value=0, max_value=10, value=0, step=1)
        
        if st.button("Confirm Downloading info"):
            list_datainfo = harmonizer.extract(url=url_1, depth=depth_1, down_ext=extensions_1, key_words=key_words_1)
            harmonizer = Harmonizer(list_datainfo)
            st.session_state.data_1 = harmonizer.transform()[0].data
            st.session_state.step = 1
    elif st.session_state.data_source1 == "local":
        pass
    elif st.session_state.data_source1 == "Col case":
        st.header("Dataset 1")
        if st.button("Load: Casos_positivos_de_COVID-19_en_Colombia"):
            load_data_1()

if st.session_state.step >= 1:
    st.subheader("Step 2: Apply NaN Threshold")
    st.slider("NaN Threshold for DataBase 1", 0, 100, 10, step=10, key="threshold_1")
    if st.button("Apply Threshold 1"):
        apply_threshold_1()
        st.session_state.step = 2

if st.session_state.step >= 2:
    st.subheader("Step 3: Select Columns of Interest")
    st.multiselect("Choose columns for Dataset 1", st.session_state.filtered_df_1.columns.tolist(), key="columns_1")
    if st.button("Confirm Column Selection 1"):
        select_columns_1()
        st.session_state.step = 3

if st.session_state.step >= 3:
    st.subheader("Step 4: Select Aggregation Functions")
    for col in st.session_state.selected_columns_1:
        st.selectbox(f"Aggregation for {col}", [mode, "mean", "sum", "min", "max"], key=f"agg_1_{col}")
    if st.button("Confirm Aggregation Functions 1"):
        select_agg_functions_1()
        st.session_state.step = 4

if st.session_state.step >= 4:
    st.subheader("Step 5: Perform Aggregation")
    col_agg = st.selectbox("Choose columnt to Group By:", st.session_state.filtered_df_1.columns)
    if st.button("Perform Aggregation 2", key="pa2"):
        perform_aggregation_1(col_agg)
        st.session_state.step = 5
    st.write(st.session_state.agg_df_1)


#######################################################################
#######################################################################
#######################################################################
#######################################################################

if st.session_state.step >= 5:
    st.subheader("Step 5: Select Data Source")
    st.session_state.data_source2 = st.selectbox("Choose data source", ["url", "local", "Col case"],key="ds2")
    if st.button("Confirm Data Source",key="dsb2"):
        st.session_state.step = 6

if st.session_state.step >= 6:
    st.subheader("Step 6: Load Data")
    harmonizer2 = Harmonizer()
    if st.session_state.data_source2 == "url":
        st.subheader("Enter URLs for datasets")
        col1, col2 = st.columns(2)
        with col1:
            url_2 = st.text_area("Enter URL for Dataset:", height=10,value=None,key="u2")
            extensions_2 = st.multiselect("Choose data source", ['.csv', '.xls', '.xlsx', ".txt", ".sav", ".zip"], default=[".csv",".zip"],key="e2")
        with col2:
            key_words_2 = st.text_area("Enter relevant keywords (separated by commas ',')", height=10,value=None,key="kw2")
            depth_2 = st.number_input('Enter a number', min_value=0, max_value=10, value=0, step=1, key="d2")
        
        if st.button("Confirm Downloading info", key="cdi2"):
            list_datainfo = harmonizer2.extract(url=url_2, depth=depth_2, down_ext=extensions_2, key_words=key_words_2)
            harmonizer2 = Harmonizer(list_datainfo)
            st.session_state.data_2 = harmonizer2.transform()[0].data
            st.session_state.step = 7
    elif st.session_state.data_source2 == "local":
        pass
    elif st.session_state.data_source2 == "Col case":
        st.header("Dataset 2")
        if st.button("Load: Censo Colombia 2018: Personas"):
            load_data_2()


if st.session_state.step >= 7:
    st.subheader("Step 7: Apply NaN Threshold")
    st.slider("NaN Threshold for DataBase 2", 0, 100, 30, step=10, key="threshold_2")
    if st.button("Apply Threshold 2"):
        apply_threshold_2()
        st.session_state.step = 8

if st.session_state.step >= 8:
    st.subheader("Step 8: Select Columns of Interest")
    st.multiselect("Choose columns for Dataset 2", st.session_state.filtered_df_2.columns.tolist(), key="columns_2")
    if st.button("Confirm Column Selection 2"):
        select_columns_2()
        st.session_state.step = 9

if st.session_state.step >= 9:
    st.subheader("Step 9: Select Aggregation Functions")
    for col in st.session_state.selected_columns_2:
        st.selectbox(f"Aggregation for {col}", [mode, ["mean", "sum", "min", "max"]], key=f"agg_2_{col}")
    if st.button("Confirm Aggregation Functions 2"):
        select_agg_functions_2()
        st.session_state.step = 10

if st.session_state.step >= 10:
    st.subheader("Step 10: Perform Aggregation")
    col_agg = st.selectbox("Choose columnt to Group By:", st.session_state.filtered_df_2.columns)
    if st.button("Perform Aggregation 1"):
        perform_aggregation_2(col_agg)
        st.write(st.session_state.agg_df_2)
        st.session_state.step = 11
        

# Merge Datasets
if st.session_state.step >= 11:
    st.header("Merge Datasets")
    if st.button("Merge Datasets"):
        merge_dataframes()
        st.session_state.step = 12

# Display Results
if st.session_state.step >= 12:
    st.header("Results")
    st.dataframe(st.session_state.merged_df)
    
    if st.button("Download Results"):
        csv = st.session_state.merged_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="merged_results.csv",
            mime="text/csv",
        )
    
    st.subheader("Start Over")
    if st.button("Reset"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]

st.write(f"Current Step: {st.session_state.step}")