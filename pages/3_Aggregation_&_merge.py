import streamlit as st
import pandas as pd
from utils import mode
from instructions import INSTRUCTIONS

st.set_page_config(page_title="Aggregation and Merge", page_icon="🧮")

st.title("Aggregation and Merge 🧮")

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown(INSTRUCTIONS["aggregation_merge"])

if len(st.session_state.Data_Bases) < 2:
    st.warning("You need at least two databases to perform aggregation and merge. Please load more data.")
else:
    st.subheader("Aggregation Process")
    
    db_index = st.selectbox("Select database to aggregate", range(len(st.session_state.Data_Bases)), format_func=lambda x: f"Database {x+1}")
    df = st.session_state.Data_Bases[db_index]

    groupby_col = st.selectbox("Select column to groupby", df.columns)
    st.session_state.merge_cols.append(groupby_col)

    agg_functions = {}
    for col in df.drop(groupby_col, axis=1).columns:
        agg_functions[col] = st.selectbox(f"Aggregation for {col}", ["mode", """["mean", "sum", "min", "max"]""", "mean", "sum", "min", "max"])
    for k,v in agg_functions.items():
        if agg_functions[k] == "mode":
            agg_functions[k] = mode
        elif agg_functions[k] == """["mean", "sum", "min", "max"]""":
            agg_functions[k] = ["mean", "sum", "min", "max"]

    if st.button("Perform Aggregation"):
        df = df.groupby(groupby_col).agg(agg_functions).reset_index()
        st.session_state.Data_Bases[db_index] = df
        st.success("Aggregation performed successfully!")
        st.write(df.head())

    st.subheader("Merge Databases")

    if st.button("Merge Databases"):
        if not isinstance(st.session_state.Merge_Base, pd.DataFrame):
            st.session_state.Merge_Base = st.session_state.Data_Bases[0].merge(st.session_state.Data_Bases[0], left_on=st.session_state.merge_cols[1],right_on=st.session_state.merge_cols[0],how='inner') 
        else: 
            st.session_state.Merge_Base = st.session_state.Merge_Base.merge(
                st.session_state.Data_Bases[-1],
                left_on=st.session_state.merge_cols[0],
                right_on=st.session_state.merge_cols[-1],
                how='inner'
            )
        st.success("Databases merged successfully!")
        st.write(st.session_state.Merge_Base.head())

