import streamlit as st
import pandas as pd
from socio4health.utils import harmonizer_utils

from utils import mode, initialize_session_state, show_session_state
from instructions import INSTRUCTIONS
from socio4health import Harmonizer  # asumiendo que tu clase se llama así

st.set_page_config(page_title="Harmonizer", page_icon="assets/s4h.ico", layout="wide")

initialize_session_state()

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

dfs = st.session_state.Data_Sources

har.similarity_threshold = similarity_threshold

if st.button("Run Vertical Merge"):
    with st.spinner("Running vertical merge..."):
        try:
            merged = har.s4h_vertical_merge(dfs)
            st.session_state.Data_Sources = merged

            st.success("Vertical merge completed!")
            st.write("Preview of merged data:")

            for i, df in enumerate(merged):
                st.write(f"DataFrame {i + 1} shape: {len(df)} rows, {len(df.columns)} columns")
                st.dataframe(df.head(5))

        except Exception as e:
            st.error(f"Error during harmonization: {e}")

st.subheader("Dictionary Grouping")
with st.expander("Dictionary Grouping Options", expanded=False):
    options = har.s4h_get_available_columns(dfs)
    extra_cols = st.multiselect("Extra Columns", options=options)
    har.extra_cols = extra_cols
    model = st.file_uploader("Choose Model", accept_multiple_files=True)
    if st.button("Run Dictionary Grouping"):
        with st.spinner("Running dictionary translation..."):
            try:
                dic = st.session_state.standardized_dict

                dic = harmonizer_utils.s4h_translate_column(dic, "question", language="en")
                dic = harmonizer_utils.s4h_translate_column(dic, "description", language="en")
                dic = harmonizer_utils.s4h_translate_column(dic, "possible_answers", language="en")
                har.dict_df = dic
                st.session_state.standardized_dict = dic

                st.success("Dictionary translation completed")
                st.write("Preview of Translated dictionary:")
                st.dataframe(dic.head(5))

            except Exception as e:
                st.error(f"Error during dictionary translation: {e}")

        with st.spinner("Running dictionary classification..."):
            try:
                dfs = harmonizer_utils.s4h_classify_rows(
                    dic,
                    "question_en",
                    "description_en",
                    "possible_answers_en",
                    new_column_name="category",
                    MODEL_PATH=model
                )

                st.session_state.Data_Sources = dfs
                st.write("Preview of Grouped data:")
                for i, df in enumerate(dfs):
                    st.write(f"DataFrame {i + 1} shape: {len(df)} rows, {len(df.columns)} columns")
                    st.dataframe(df.head(5))

                st.success("Dictionary classification completed")
                st.write("Preview of classified dictionary:")
                st.dataframe(dic.head(5))

            except Exception as e:
                st.error(f"Error during dictionary classification: {e}")

st.subheader("Data Selector")
with st.expander("Data Joining Options", expanded=False):
    category = st.multiselect(
        "Categories",
        options=[
            "Business", "Education", "Fertility", "Housing",
            "Identification", "Migration", "Nonstandard job", "Social Security"
        ],
        default=[
            "Business", "Education", "Fertility", "Housing",
            "Identification", "Migration", "Nonstandard job", "Social Security"
        ]
    )
    har.categories = [str(category)]
    har.key_col = st.selectbox("Column Selection", options=options, index=0)
    har.key_val = st.text_input("Values (comma separated)").split(',')

    if st.button("Run Data Selector"):
        if not har.categories or not har.key_col or not har.key_val:
            st.error("Please select at least one category, one column, and provide values.")
            st.stop()
        with st.spinner("Running data selector..."):
            try:
                dfs = st.session_state.Data_Sources
                filtered_dask_dfs = har.s4h_data_selector(dfs)
                st.session_state.Data_Sources = filtered_dask_dfs

                st.success("Data selection completed!")
                st.write("Preview of filtered data:")
                for i, df in enumerate(filtered_dask_dfs):
                    st.write(f"DataFrame {i + 1} shape: {len(df)} rows, {len(df.columns)} columns")
                    st.dataframe(df.head(5))

            except Exception as e:
                st.error(f"Error during data selection: {e}")


st.subheader("Data Joining")
with st.expander("Data Joining Options", expanded=False):
    join_key = st.selectbox("Join Key", options=options, index=0)
    aux_key = st.selectbox("Auxiliar Key", options=options)
    har.join_key = join_key
    har.aux_key = aux_key

show_session_state()

