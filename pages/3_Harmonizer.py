import streamlit as st
import pandas as pd
from utils import mode
from instructions import INSTRUCTIONS
from socio4health import Harmonizer  # asumiendo que tu clase se llama así

st.set_page_config(page_title="Harmonizer", page_icon="🎵", layout="wide")

# Initialize session state
if 'Data_Sources' not in st.session_state:
    st.session_state.Data_Sources = []
if "colnames" not in st.session_state:
    st.session_state.colnames = None
if "colspecs" not in st.session_state:
    st.session_state.colspecs = None
if "standardized_dict" not in st.session_state:
    st.session_state.standardized_dict = None
if "harmonized_data" not in st.session_state:
    st.session_state.harmonized_data = None

st.title("Harmonizer 🎵")

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown(INSTRUCTIONS["aggregation_merge"])

st.subheader("Vertical Merge")

if not st.session_state.Data_Sources:
    st.warning("⚠️ No data sources loaded. Please upload data first.")
    st.stop()

if st.session_state.standardized_dict is None:
    st.warning("⚠️ No standardized dictionary found. Please standardize a dictionary first.")
    st.stop()

har = Harmonizer()
har.dict_df = st.session_state.standardized_dict

similarity_threshold = st.slider(
    "Similarity Threshold",
    min_value=0.0, max_value=1.0, value=0.9, step=0.05
)

#  TODO Selectable keys based on data sources
join_key = st.text_input("Join Key", value="DIRECTORIO")
aux_key = st.text_input("Auxiliary Key", value="ORDEN")
extra_cols = st.multiselect("Extra Columns", options=["ORDEN"], default=["ORDEN"])

# Apply parameters
har.similarity_threshold = similarity_threshold
har.join_key = join_key
har.aux_key = aux_key
har.extra_cols = extra_cols

# Run vertical merge
if st.button("Run Vertical Merge"):
    with st.spinner("Running vertical merge..."):
        try:
            dfs = st.session_state.Data_Sources
            merged = har.s4h_vertical_merge(dfs)
            st.session_state.harmonized_data = merged

            st.success("Vertical merge completed!")
            st.write("Preview of merged data:")
            st.dataframe(merged.head())

        except Exception as e:
            st.error(f"Error during harmonization: {e}")

st.subheader("Dictionary Grouping")

st.subheader("Data Joining")


