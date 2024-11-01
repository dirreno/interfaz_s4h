import streamlit as st
import streamlit as st
import pandas as pd
from nyctibius import BirdAgent
from utils import *

ss = st.session_state
 
# Initialize session state
if 'state' not in ss:
    ss.state = 'Start'
if 'prev_state' not in ss:
    ss.prev_state = []
if 'Data_Bases' not in ss:
    ss.Data_Bases = []
if 'Merge_Base' not in ss:
    ss.Merge_Base = None
if 'merge_cols' not in ss:
    ss.merge_cols = []
if 's2s_data' not in ss:
    ss.s2s_data = None
if 'messages' not in ss:
    ss.messages = []
if 'groq_key' not in ss:
    ss.groq_key = None


st.sidebar.markdown('</a> Developed by Harmonize. Contact: <a style="text-align: center;padding-top: 0rem;" href="mailto: es.lozano@uniandes.edu.com">:email:', unsafe_allow_html=True)
with st.sidebar:
    ss.groq_key = st.text_input(label = ":key: Groq Key:", help="Required for Chat with data.",type="password")

# Define states
states = [
    'Start',
    'Data Source Selection',
    'Data Loading',
    'Threshold',
    'Filter',
    'Chat or Agg',
    'Chat',
    'Agg selection',
    'Agg perform',
    'Merge',
    'Finish'
]

# Function to move to the next state
def next_state(state = None):
    if not state:
        current_index = states.index(ss.state)
        ss.prev_state = states[current_index]
        if current_index < len(states) - 1:
            ss.state = states[current_index + 1]
            ss.prev_state = []
    else:
        ss.prev_state = ss.state
        ss.state = state


# Main app
st.title("Socio4Health Data Analysis")

# State machine logic
if ss.state == 'Start':
    st.subheader("Welcome to the Data Analysis Pipeline")
    if st.button("Begin Analysis"):
        next_state()

if ss.state == 'Data Source Selection':
    st.subheader(f"DB: {len(ss.Data_Bases)+1} → Select Data Source")
    if len(ss.Data_Bases) == 0:
        col_case = "Col case: Covid19 Data"
    else:
        col_case = "Col case: Col People Census Data"
    ss.s2s_data = st.selectbox("Choose data source", ["url", "local", col_case, "Test"], key="CDS1")
    if st.button("Proceed to Data Loading"):
        next_state()

if ss.state == 'Data Loading':
    st.subheader(f"DB: {len(ss.Data_Bases)+1} → Load Data")
    ss.Data_Bases.append(load_data(ss.s2s_data))
    if st.button("Move to Data Filtering") and isinstance(ss.Data_Bases[len(ss.Data_Bases)-1], pd.DataFrame):
        st.write(ss.Data_Bases[len(ss.Data_Bases)-1].head())
        next_state()

if ss.state == 'Threshold':
    st.subheader(f"DB: {len(ss.Data_Bases)+1} → Filter: Trheshold for NaN values in columns") 
    
    threshold = st.slider("NaN Threshold for DataBase", 0, 100, 10, step=10)
    if st.button("Apply Threshold 1", key="t"):
        ss.Data_Bases[len(ss.Data_Bases)-1] = filter_columns_by_nan_threshold(ss.Data_Bases[len(ss.Data_Bases)-1], threshold)
        next_state()

if ss.state == "Filter":
    st.subheader(f"DB: {len(ss.Data_Bases)+1} → Filtering columns")
    columns = st.multiselect("Choose columns for Dataset ", ss.Data_Bases[len(ss.Data_Bases)-1].columns, key="SCF")
    if st.button("Continue to Options") and ss["SCF"]:
        ss.Data_Bases[len(ss.Data_Bases)-1] =  ss.Data_Bases[len(ss.Data_Bases)-1].loc[:,ss["SCF"]]
        if len(ss.Data_Bases)-1<=1:
            next_state()
        else:
            next_state("Agg selection")
    else:
        st.write("Please select at least one column")

if ss.state == 'Chat or Agg':
    st.subheader("Select an Option")
    option = st.radio('Choose one:', ['Chat with data','Perform aggregation'])
    if st.button("Option chose"):
        if option == 'Perform aggregation':
            next_state("Agg selection")
        else:        
            next_state()

if ss.state == 'Chat':
    st.subheader("Chat with your data")
    llm = ChatGroq(
        model_name="mixtral-8x7b-32768", 
        api_key = "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")
    if isinstance(ss.Merge_Base, pd.DataFrame):
        #agent = BirdAgent(dfs=ss.Merge_Base)

        agent = Agent(ss.Merge_Base, config={"llm": llm})
    else:
        st.subheader("Chat with your data")
        #agent = BirdAgent(dfs=ss.Data_Bases[len(ss.Data_Bases)-1])
        agent = Agent(ss.Data_Bases, config={"llm": llm})

    for message in ss.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    ss.messages.append({"role": "assistant", "content": "Hello! Let’s dive into your data"})
    # React to user input
    if prompt := st.chat_input("What is your question?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        ss.messages.append({"role": "user", "content": prompt})
        # Get bot response
        response = get_bot_response(agent, prompt)
        
        # Display bot response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add bot response to chat history
        ss.messages.append({"role": "assistant", "content": st.write(response)})

    if len(ss.messages)>1:# Add a button to clear chat history
        if st.button("Clear Chat History", key="cch1"):
            ss.messages = []
            st.rerun()
    if st.button("Continue to Aggregation") and not ss.prev_state:
        next_state()
    else:
        pass # no se que iria despues


if ss.state == 'Agg selection':
    st.subheader("Agregation process: Select column to groupby")
    st.selectbox("Select column to groupby", ss.Data_Bases[len(ss.Data_Bases)-1].columns, key="SCGB")
    ss.merge_cols.append(ss["SCGB"])
    st.subheader("Agregation process: Select agg functions per column")
    for col in ss.Data_Bases[len(ss.Data_Bases)-1].columns:
        st.selectbox(f"Aggregation for {col}", [mode, "mean", "sum", "min", "max"], key=f"agg_1_{col}")
    
    if st.button("Continue to select agg functions"):
        next_state()

if ss.state == 'Agg perform':
    st.subheader("Agregation process: Partial result")


    try:
        agg_functions = {col: ss[f"agg_1_{col}"] for col in ss.Data_Bases[len(ss.Data_Bases)-1].columns}
        ss.Data_Bases[len(ss.Data_Bases)-1] = ss.Data_Bases[len(ss.Data_Bases)-1].groupby(ss["SCGB"]).agg(agg_functions).drop(ss["SCGB"], axis=1)
    except:
        pass    
    st.write(ss.Data_Bases[len(ss.Data_Bases)-1].head())
    
    if len(ss.Data_Bases)-1 > 1:
        if st.button("Continue to merge process"):
            next_state()
    else:
        if st.button("Continue to load next db"):
            next_state("Data Source Selection")

if ss.state == 'Merge':
    st.subheader("Merge databases")

    if not isinstance(ss.Merge_Base,pd.DataFrame):
        ss.Merge_Base = pd.merge(ss.Data_Bases[0], ss.Data_Bases[1], 
                                            left_on=ss.merge_cols[0], right_on=ss.merge_cols[1], how='inner')
    else:
        ss.Merge_Base = pd.merge(ss.Merge_Base, ss.Data_Bases[-1], 
                                            left_on=ss.merge_cols[0], right_on=ss.merge_cols[-1], how='inner')

    st.write(ss.Data_Bases[0].head())
    if st.button("Chat with Merged data"):
        next_state('Chat')

if ss.state == 'Finish':
    st.subheader("Analysis Complete")
    if st.button("Restart Analysis"):
        next_state('Start')

# Add a section to display the progress
st.write(f"Current State: {ss.state} # {states.index(ss.state)}")