import streamlit as st
import pandas as pd
import socio4health as s4h
from streamlit.components.v1 import html
import json

def initialize_session_state():
    if 'Data_Sources' not in st.session_state:
        st.session_state.Data_Sources = []
    if 'standardized_dict' not in st.session_state:
        st.session_state.standardized_dict = None
    if "is_fwf" not in st.session_state:
        st.session_state.is_fwf = False
    if "colnames" not in st.session_state:
        st.session_state.colnames = None
    if "colspecs" not in st.session_state:
        st.session_state.colspecs = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def show_session_state():
    st.sidebar.header("Session State")

    if st.session_state.standardized_dict is not None:
        st.sidebar.write("Standardized Dictionary: Loaded" if st.session_state.standardized_dict is not None else "Not Loaded")

    if st.session_state.is_fwf:
        st.sidebar.write("Colnames Loaded" if st.session_state.colnames is not None else "No Colnames Loaded")
        st.sidebar.write("Colspecs Loaded" if st.session_state.colspecs is not None else "No Colspecs Loaded")

    if st.session_state.Data_Sources:
        st.sidebar.write(f"Total databases loaded: {len(st.session_state.Data_Sources)}")
        st.sidebar.subheader("Loaded Data Sources:")
        for i, df in enumerate(st.session_state.Data_Sources):
            st.sidebar.write(f"DataFrame {i + 1} shape: {len(df)} rows, {len(df.columns)} columns")

    #st.session_state.get("messages", []),

def mode(series):
    mode = series.mode()
    if len(mode) > 1:
        return ','.join(mode)
    else:
        return mode.iloc[0]

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
        height= 250,
    )

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url("https://raw.githubusercontent.com/harmonize-tools/socio4health/main/docs/source/_static/image.png");
                background-repeat: no-repeat;
                padding-top: 120px;
                background-position: 20px 20px;
                background-size: 70px 70px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "Socio4Health";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )