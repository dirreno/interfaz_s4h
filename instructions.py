INSTRUCTIONS = {
    "home_page": """
# Socio4Health Data Analysis Pipeline

## Getting Started
1. Review the workflow diagram to understand the process
2. Check available datasets in the system
3. Make sure you have your Groq API key ready
4. Use the sidebar stepper to track your progress

## Available Features
- Data Loading from multiple sources
- Data Filtering and cleaning
- Record stacking and combining
- Data aggregation and merging
- AI-powered chat analysis

## Available Datasets
- COVID-19 Colombian Data
- Colombian People Census Data
- Custom datasets (upload your own)
    """,
    
    "data_loading": """
# Data Loading Instructions

## Choose Your Data Source:
1. URL Source:
   - Enter website URL
   - Select file extensions (.csv, .xls, etc.)
   - Add relevant keywords
   - Set crawling depth
   - Click "Confirm Downloading"

2. Local Files:
   - Click "Choose a CSV file"
   - Select your file
   - Wait for upload

3. Example Datasets:
   - Choose from Colombian datasets
   - Data loads automatically

## Tips:
- Ensure clean, properly formatted data
- Check for encoding issues
- Use appropriate file extensions
- Verify data preview before proceeding
    """,
    
    "data_filtering": """
# Data Filtering Instructions

## Steps:
1. Select Database to Filter:
   - Choose from loaded databases
   - Review initial data preview

2. NaN Threshold:
   - Use slider (0-100%)
   - Higher = more columns removed
   - Click "Apply Threshold"

3. Column Selection:
   - Choose columns to keep
   - Review selections
   - Click "Apply Column Filter"

## Tips:
- Start with conservative threshold
- Review column stats before filtering
- Keep track of removed columns
    """,
    
    "add_records": """
# Add Records Instructions

## Stacking Similar Datasets:
1. Select Databases:
   - Choose multiple databases
   - Ensure similar structure
   - Review column comparison

2. Configure Stacking:
   - Select common columns
   - Choose identifier type:
     * Automatic Index
     * Custom Labels
     * Date Values

3. Execute:
   - Click "Stack Datasets"
   - Review statistics
   - Verify preview

## Tips:
- Verify column compatibility
- Use meaningful identifiers
- Back up data before stacking
    """,
    
    "aggregation_merge": """
# Aggregation & Merge Instructions

## Aggregation Process:
1. Select database to aggregate
2. Choose groupby column
3. Set aggregation functions:
   - Mode
   - Mean
   - Sum
   - Min/Max
   - Multiple functions

## Merging Process:
1. Ensure 2+ databases loaded
2. Select merge columns
3. Choose merge type
4. Execute merge
5. Review results

## Tips:
- Choose appropriate aggregations
- Verify merge keys are unique
- Check for data loss
    """,
    
    "chat": """
# Chat with Data Instructions

## Setup:
1. Enter Groq API key in sidebar
2. Select database to analyze
3. Review data preview

## Usage:
1. Type questions naturally
2. Review AI responses
3. Ask follow-ups
4. Clear history if needed

## Tips:
- Be specific in questions
- Use clear language
- Review data structure first
- Check API key if not working
    """,
    
    "common_issues": """
# Common Issues and Solutions

1. Data Loading Fails:
   - Check file format/encoding
   - Verify URL accessibility
   - Check internet connection

2. Filtering Issues:
   - Reduce NaN threshold
   - Check column data types
   - Verify column names

3. Stacking Errors:
   - Confirm similar structure
   - Check matching data types
   - Verify memory sufficient

4. Merge Problems:
   - Check matching columns
   - Look for duplicate keys
   - Ensure enough memory

5. Chat Issues:
   - Verify API key
   - Check connection
   - Simplify questions
    """
}

# Usage example:
"""
import streamlit as st

# In your specific page, use like this:
st.markdown(INSTRUCTIONS["home_page"])

# Or with expander:
with st.expander("See Instructions"):
    st.markdown(INSTRUCTIONS["data_loading"])

# Or in multiple columns:
col1, col2 = st.columns(2)
with col1:
    st.markdown(INSTRUCTIONS["data_filtering"])
with col2:
    st.markdown(INSTRUCTIONS["chat"])
"""