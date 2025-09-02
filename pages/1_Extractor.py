from pathlib import Path

import streamlit as st
import os
import tempfile
from utils import initialize_session_state
from instructions import INSTRUCTIONS
from socio4health import Extractor

st.set_page_config(page_title="Data Extraction", page_icon="📥", layout="wide")

initialize_session_state()

# Initialize Data_Bases if not exists
if 'Data_Bases' not in st.session_state:
    st.session_state.Data_Bases = []

st.title("Data Extraction 📥")

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown(INSTRUCTIONS["data_loading"])

if 'state' not in st.session_state:
    st.session_state.state = "Select Source"
if 'source_data' not in st.session_state:
    st.session_state.source_data = "Select an Option"

st.session_state.source_data = st.selectbox(
    "Choose data source",
    ["Select an Option", "Internet (URL)", "Local file"]
)


def handle_extraction(extractor, source_type):
    try:
        with st.spinner(f"Extracting data from {source_type}..."):
            result = extractor.extract()

        if result:
            st.success("Data extraction completed successfully!")

            if isinstance(result, list):
                st.session_state.Data_Bases.extend(result)
                st.info(f"Added {len(result)} datasets to your workspace")
            else:
                st.session_state.Data_Bases.append(result)
                st.info("Added 1 dataset to your workspace")

            return True
        else:
            st.error("No data was extracted. Please check your input parameters.")
            return False

    except Exception as e:
        st.error(f"Error during extraction: {str(e)}")
        return False


def render_csv_options():
    csv_options = st.expander("CSV Options", expanded=False)
    with csv_options:
        sep = st.text_input("Separator", value=",", key="csv_sep")
        encoding = st.selectbox(
            "Encoding",
            ['utf-8', 'latin1', 'iso-8859-1', 'cp1252'],
            key="csv_encoding"
        )
    return sep, encoding

def render_fwf_options():
    is_fwf = st.toggle("Is a fixed width file?")
    if is_fwf:
        #TODO Add fixed width file options
        st.write("Fixed width file options would go here")
        return True
    return False

def render_extensions(detected_exts = ('.csv', '.zip')):
    extensions = st.multiselect(
        "File extensions to look for",
        ['.csv', '.xls', '.xlsx', '.txt', '.sav', '.zip', '.7z', '.tar', '.gz', '.tgz'],
        default=detected_exts,
        key="extensions"
    )
    return extensions

is_fwf = False

if st.session_state.source_data == "Internet (URL)":
    st.subheader("Enter URLs for datasets")

    col1, col2 = st.columns(2)
    with col1:
        url = st.text_input(
            "Enter URL for Dataset:",
            value="https://microdatos.dane.gov.co/index.php/catalog/663",
            key="url_input"
        )

        extensions = render_extensions()

        if any(ext in ['.txt'] for ext in extensions):
            is_fwf = render_fwf_options()
        if any(ext in ['.csv', '.txt'] for ext in extensions):
            sep, encoding = render_csv_options()

    with col2:
        key_words = st.text_input(
            "Enter relevant keywords (separated by commas)",
            value="",
            key="keywords"
        )
        depth = st.number_input(
            'Scraping depth',
            min_value=0, max_value=10, value=1, step=1,
            key="depth"
        )

    if st.button("Extract Data from URL"):
        if url and url.strip():
            extractor = Extractor(
                input_path=url,
                down_ext=extensions,
                sep=sep,
                encoding=encoding,
                output_path="./data",
                depth=depth,
                key_words=[kw.strip() for kw in key_words.split(",")] if key_words else None,
                is_fwf = is_fwf
            )

            # Perform extraction
            if handle_extraction(extractor, "URL"):
                st.session_state.state = "Data Loaded"
                st.rerun()

        else:
            st.warning("Please enter a valid URL")

elif st.session_state.source_data == "Local file":
    st.subheader("Upload local files")

    uploaded_files = st.file_uploader(
        "Choose file",
        type=['csv', 'xlsx', 'xls', 'txt', 'sav', 'zip', '7z', 'tar', 'gz', 'tgz'],
        accept_multiple_files=True,
        key="file_uploader"
    )


    files_extensions = [os.path.splitext(f.name)[1].lower() for f in uploaded_files] if uploaded_files else []
    extensions = files_extensions

    if files_extensions == '.zip' and uploaded_files is not None:
        extensions = render_extensions(extensions)

    if any(ext in ['.txt'] for ext in extensions):
        is_fwf = render_fwf_options()

    sep = ','
    encoding = 'utf-8'
    if any(ext in ['.csv', '.txt'] for ext in extensions):
        sep, encoding = render_csv_options()

    if uploaded_files is not None and st.button("Process Local Files"):
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                for uploaded_file in uploaded_files:
                    file_path = Path(temp_dir) / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                # Pass the temporary folder path to the Extractor
                extractor = Extractor(
                    input_path=temp_dir,
                    down_ext=extensions,
                    sep=sep,
                    output_path="./data",
                    encoding=encoding,
                    is_fwf=is_fwf
                )
                dask_dfs = extractor.extract()

            except Exception as e:
                st.error(f"Failed to process {os.path.basename(file_path)}: {str(e)}")


st.sidebar.header("Data Summary")
st.sidebar.write(f"Total databases loaded: {len(st.session_state.Data_Bases)}")

if st.session_state.Data_Bases:
    st.sidebar.subheader("Loaded Databases")
    for i, db in enumerate(st.session_state.Data_Bases):
        if hasattr(db, 'shape'):
            st.sidebar.write(f"DB {i + 1}: {db.shape[0]} rows × {db.shape[1]} columns")
        elif isinstance(db, dict):
            st.sidebar.write(f"DB {i + 1}: Dictionary with {len(db)} keys")
        else:
            st.sidebar.write(f"DB {i + 1}: {type(db).__name__}")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)