import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from utils import initialize_session_state
from utils import load_covidcol_data, Harmonizer
from instructions import INSTRUCTIONS

def perform_eda(df):
    """
    Perform exploratory data analysis on the loaded dataframe
    """
    st.subheader("📊 Exploratory Data Analysis")
    
    # Basic Dataset Information
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Number of Rows", df.shape[0])
    with col2:
        st.metric("Number of Columns", df.shape[1])
    with col3:
        st.metric("Memory Usage (MB)", round(df.memory_usage().sum() / 1024**2, 2))

    # Data Overview
    with st.expander("📋 Data Overview", expanded=True):
        st.write("First few rows of the dataset:")
        st.dataframe(df.head())
        
        st.write("Data Types and Non-Null Counts:")
        buffer = pd.DataFrame({
            'Data Type': df.dtypes,
            'Non-Null Count': df.count(),
            'Null Count': df.isna().sum(),
            'Null Percentage': (df.isna().sum() / len(df) * 100).round(2)
        })
        st.dataframe(buffer)

    # Numerical Analysis
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numerical_cols) > 0:
        with st.expander("📈 Numerical Columns Analysis", expanded=True):
            st.write("Statistical Summary of Numerical Columns:")
            st.dataframe(df[numerical_cols].describe())
            
            # Distribution plots
            st.write("Distribution Plots:")
            default_cols = numerical_cols[:min(3, len(numerical_cols))]
            cols_to_plot = st.multiselect(
                "Select columns to plot distribution",
                options=numerical_cols,
                default=default_cols
            )
            
            if cols_to_plot:
                fig, axes = plt.subplots(1, len(cols_to_plot), figsize=(5*len(cols_to_plot), 4))
                if len(cols_to_plot) == 1:
                    axes = [axes]
                    
                for ax, col in zip(axes, cols_to_plot):
                    sns.histplot(data=df, x=col, ax=ax)
                    ax.set_title(f'Distribution of {col}')
                    plt.xticks(rotation=45)
                st.pyplot(fig)
                plt.close()

    # Categorical Analysis
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if len(categorical_cols) > 0:
        with st.expander("📊 Categorical Columns Analysis", expanded=True):
            st.write("Value Counts for Categorical Columns:")
            selected_cat_col = st.selectbox(
                "Select categorical column",
                options=categorical_cols
            )
            
            if selected_cat_col:
                value_counts = df[selected_cat_col].value_counts()
                fig, ax = plt.subplots(figsize=(10, 6))
                value_counts.plot(kind='bar')
                plt.title(f'Value Counts for {selected_cat_col}')
                plt.xticks(rotation=45)
                st.pyplot(fig)
                plt.close()
                
                st.write("Top 10 Categories:")
                st.dataframe(value_counts.head(10))

    # Correlation Analysis
    if len(numerical_cols) > 1:
        with st.expander("🔄 Correlation Analysis", expanded=True):
            correlation_matrix = df[numerical_cols].corr()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
            plt.title('Correlation Matrix')
            st.pyplot(fig)
            plt.close()

    # Missing Values Analysis
    with st.expander("❓ Missing Values Analysis", expanded=True):
        missing_data = pd.DataFrame({
            'Missing Values': df.isnull().sum(),
            'Percentage': (df.isnull().sum() / len(df) * 100).round(2)
        }).sort_values('Percentage', ascending=False)
        
        st.write("Missing Values Summary:")
        st.dataframe(missing_data[missing_data['Missing Values'] > 0])
        
        if missing_data['Missing Values'].sum() > 0:
            fig, ax = plt.subplots(figsize=(10, 6))
            missing_data[missing_data['Missing Values'] > 0]['Percentage'].plot(kind='bar')
            plt.title('Missing Values Percentage by Column')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            plt.close()

# Main script
st.set_page_config(page_title="Data Loading", page_icon="🗃️")

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown(INSTRUCTIONS["data_loading"])

initialize_session_state()
if 'state' not in st.session_state:
    st.session_state.state = "Select Source"

states = ["Select Source", "Load Data"]

st.title("Data Loading 🗃️")
st.subheader(f"Data Base: {len(st.session_state.Data_Bases)+1} → Select Data Source")

st.session_state.source_data = st.selectbox("Choose data source", ["Select an Option","Internet (URL)", "Local file", "Col case: Census & Covid19", "Health Data", "Test"])

if st.session_state.state == "Select Source":
    if st.button("Load Data"):
        st.session_state.state = "Load Data"
        
if st.session_state.state == "Load Data":
    source = st.session_state.source_data

    data = None
    harmonizer = Harmonizer()
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
            list_datainfo = harmonizer.extract(url=url_1, depth=depth_1, down_ext=extensions_1, key_words=key_words_1)
            harmonizer = Harmonizer(list_datainfo)
            data = harmonizer.transform()[0].data
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