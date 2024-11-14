import streamlit as st
import pandas as pd
from utils import filter_columns_by_nan_threshold
from instructions import INSTRUCTIONS

st.set_page_config(page_title="Data Filtering", page_icon="🪄")

st.title("Data Filtering 🪄")

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown(INSTRUCTIONS["data_filtering"])

if not st.session_state.Data_Bases:
    st.warning("No data loaded. Please load data first.")
else:
    db_index = st.selectbox("Select database to filter", range(len(st.session_state.Data_Bases)), format_func=lambda x: f"Database {x+1}")
    df = st.session_state.Data_Bases[db_index]
    st.write(df.head())

    st.subheader("Filter: Threshold for NaN values in columns")
    threshold = st.slider("NaN Threshold for DataBase", 0, 100, 10, step=10)
    
    if st.button("Apply Threshold"):
        df = filter_columns_by_nan_threshold(df, threshold)
        st.session_state.Data_Bases[db_index] = df
        st.success("Threshold applied successfully!")

    st.subheader("Filter columns")
    columns = st.multiselect("Choose columns for Dataset", df.columns)
    
    if st.button("Apply Column Filter") and columns:
        df = df.loc[:, columns]
        st.session_state.Data_Bases[db_index] = df
        st.success("Columns filtered successfully!")
        st.write(df.head())

