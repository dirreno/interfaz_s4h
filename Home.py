import streamlit as st
from utils import initialize_session_state, mermaid, add_logo
import extra_streamlit_components as stx
from instructions import INSTRUCTIONS


st.set_page_config(page_title="Socio4Health Data Analysis", page_icon="assets/s4h.ico", layout="wide")

add_logo()

# Initialize session state
initialize_session_state()

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown(INSTRUCTIONS["home_page"])

# Sidebar
st.sidebar.markdown('Developed by Harmonize team')
st.sidebar.markdown('<a href="mailto:d.irrenotorres@uniandes.edu.co">:email: Contact Us</a>', unsafe_allow_html=True)


# Main content
st.title("Socio4Health Data Analysis 🏘️👥🏥")

st.markdown("""
Welcome to the Socio4Health Data Analysis Pipeline! This powerful tool empowers you to explore, analyze, and gain insights from health-related datasets.
""")

# Workflow diagram
st.header("🔀 Workflow Diagram")

# Use Mermaid diagram for Streamlit 1.10.0 and newer
workflow = """
graph LR
    A[Load Data] --> B[Filter Data]
    B --> C[Chat with Data]
    B --> D[Aggregate & Merge]
    B --> E[Stack Data]
    E --> C
    D --> C
    C --> F[Insights]
"""
mermaid(workflow)

# Getting Started Guide
st.header("🚀 Getting Started")
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Data Loading")
    st.markdown("""
    - Navigate to the 'Data Loading' page
    - Choose your data source
    - Load one or more datasets
    """)
    
    st.subheader("2. Data Filtering")
    st.markdown("""
    - Go to the 'Data Filtering' page
    - Set NaN threshold for columns
    - Select specific columns to keep
    """)

with col2:
    st.subheader("3. Chat with Data")
    st.markdown("""
    - Visit the 'Chat' page
    - Ask questions about your data
    - Get AI-powered insights
    """)
    
    st.subheader("4. Aggregation & Merge")
    st.markdown("""
    - Use the 'Aggregation and Merge' page
    - Perform data aggregations
    - Merge multiple datasets
    """)


# Tips and Notes
st.header("💡 Tips")
tips = st.container()

with tips:
    tip1, tip2, tip3 = st.columns(3)
    
    with tip1:
        st.info("**Data Types**: The app supports various data formats including CSV, Excel, and databases.")
    
    with tip2:
        st.warning("**API Key**: Don't forget to enter your Groq API key in the sidebar for chat functionality.")
    
    with tip3:
        st.success("**Save Your Work**: You can download processed data at various stages of the analysis.")

# Dataset Information
st.header("📚 Available Datasets")
st.markdown("""
The following datasets are currently available for analysis:
- COVID-19 Colombian Data
- Colombian People Census Data
- Custom datasets (upload your own)

Explore these datasets to uncover valuable insights about public health and demographics.
""")