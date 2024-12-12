import streamlit as st
from tqdm import tqdm
import pandas as pd
from nyctibius import Harmonizer
from langchain_groq.chat_models import ChatGroq
from pandasai import Agent
from streamlit.components.v1 import html
from pandasai.responses.response_parser import ResponseParser
import json

def initialize_session_state():
    if 'Data_Bases' not in st.session_state:
        st.session_state.Data_Bases = []
    if 'Merge_Base' not in st.session_state:
        st.session_state.Merge_Base = None
    if 'merge_cols' not in st.session_state:
        st.session_state.merge_cols = []
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'groq_key' not in st.session_state:
        st.session_state.groq_key = None
    if 'chat_df' not in st.session_state:
        st.session_state.chat_df = None
    if "source_data" not in st.session_state:
        st.session_state.source_data = None

def threshold_data(df):
    threshold = st.slider("NaN Threshold for DataBase", 0, 100, 10, step=10)
    if st.button("Apply Threshold 1", key="t"):
        return filter_columns_by_nan_threshold(df, threshold)
        
def filter_columns(df):
    columns = st.multiselect("Choose columns for Dataset ", df.columns)
    if st.button("Select Columns", key="c"):
        return df.loc[:,columns]

def mode(series):
    mode = series.mode()
    if len(mode) > 1:
        return ','.join(mode)
    else:
        return mode.iloc[0]
    
def filter_columns_by_nan_threshold(dataframe, threshold):
    nan_percentage = dataframe.isna().mean() * 100
    filtered_columns = nan_percentage[nan_percentage < threshold].index
    return dataframe[filtered_columns]

@st.cache_data
def load_covidcol_data():
    dfs = [pd.read_csv("data/Test_Censo_col_mini.csv"),pd.read_csv("data/Test_Censo_col_mini_cundinamarca.csv")]
    return [pd.concat(dfs, ignore_index=True),pd.read_csv("data/Test_Covid_col_mini.csv", low_memory=False)]

# Function to generate bot response
def get_bot_response(agent, user_input):
    user_input = user_input.lower()
    if "hello" in user_input or "hi" == user_input:
        return "Hello! How can I help you today?"
    elif "how are you" in user_input:
        return "I'm doing well, thank you for asking. How about you?"
    elif "bye" in user_input or "goodbye" in user_input:
        return "Goodbye! Have a great day!"
    elif "name" in user_input:
        return "My name is ChatBot. Nice to meet you!"
    else:
        return agent.chat(user_input)

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

# Handle response messages according to type: dataframe, plot or text
class MyStResponseParser(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)
    def parse(self, result):
        if result['type'] == "dataframe":
            st.dataframe(result['value'])
        elif result['type'] == 'plot':
            st.image(result["value"])
        else:
            st.write(result['value'])
        return result

def extract_json_from_response(response):
    """Extract JSON from LLM response, handling different response formats."""
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > 0:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            return None
    return None

def generate_column_descriptions(data, model):
    """Generate descriptions for columns using LLM."""
    data_info = f"Column names: {', '.join(data.columns)}\n\n"
    data_info += "Sample data (first 5 rows):\n"
    data_info += data.head().to_string()
    
    prompt = f"""As a data analyst, generate clear descriptions for each column in this dataset.
    
Data Information:
{data_info}

Instructions:
1. For each column, write a clear 1-2 sentence description explaining what the data represents
2. Format your response as a JSON object where keys are column names and values are descriptions
3. Focus on the practical meaning and use of each column
4. Be concise but informative

Example format:
{{
    "column_name": "This column represents... It is used for...",
    "another_column": "Contains information about... Used to track..."
}}

Provide only the JSON response without any additional text."""

    try:
        response = model.invoke(prompt)
        descriptions = extract_json_from_response(response)
        
        if descriptions is None:
            st.error("Failed to generate proper descriptions. Using default ones.")
            descriptions = {col: f"Description for {col}" for col in data.columns}
        
        for col in data.columns:
            if col not in descriptions:
                descriptions[col] = f"Description for {col}"
                
        return descriptions
    
    except Exception as e:
        st.error(f"Error in description generation: {str(e)}")
        return {col: f"Description for {col}" for col in data.columns}