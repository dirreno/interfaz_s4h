import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
from tqdm import tqdm
from nyctibius import Harmonizer
from nyctibius import BirdAgent
from utils import *

ss = st.session_state
if 'state' not in ss:
    ss.state = "State: Data Source 1"
if "state_list" not in ss:
    ss.state_list = ["State: Data Source 1"]


# Set page configuration
st.set_page_config(page_title="Demo4Health Data Analysis", layout="wide", page_icon="🏘")


def next_state(str_nextstep):
    if str_nextstep not in ss.state_list:
        ss.state = str_nextstep
        ss.state_list.append(ss.state)
    else:
        # If the state already exists, truncate the list up to that state
        index = ss.state_list.index(str_nextstep)
        ss.state_list = ss.state_list[:index + 1]
        ss.state = str_nextstep

# Main content
st.title("Socio4Health Data Analysis")
st.write(ss.state)
st.write(ss.state_list)


# New initial state: Select data source
if ss.state == "State: Data Source 1" or ("State: Data Source 1" in ss.state_list):
    st.subheader("state 0: Select Data Source")
    if st.button("Next Step",key="SDS1"):
        next_state("State: Load Data 1")

if ss.state == "State: Load Data 1" or ("State: Load Data 1" in ss.state_list):
    st.subheader("state 1: Load Data")
    next_state("State: Apply NaN Threshold 1")
            
if ss.state == "State: Apply NaN Threshold 1" or ("State: Apply NaN Threshold 1" in ss.state_list):
    st.subheader("state 2: Apply NaN Threshold")
    if st.button("Apply Threshold 1", key="at1"):
        next_state("State: Select Columns of Interest 1")

if ss.state == "State: Select Columns of Interest 1" or ("State: Select Columns of Interest 1" in ss.state_list):
    st.subheader("state 3: Select Columns of Interest")
    if st.button("Confirm Column Selection 1", key="ccs1"):
        next_state("State: Perform aggregation or Chat with data")

if ss.state == "State: Perform aggregation or Chat with data" or ("State: Perform aggregation or Chat with data" in ss.state_list):
    st.subheader("state 4: Perform aggregation or Chat with data")
    option = st.radio('Choose one:', ['Chat with data','Perform aggregation'])
    if option == 'Perform aggregation':
        next_state("State: Select Aggregation Functions 1")
    else:        
        pass

if ss.state == "State: Select Aggregation Functions 1" or ("State: Select Aggregation Functions 1" in ss.state_list):
    
    st.subheader("state 4: Select Aggregation Functions")
    if st.button("Confirm Aggregation Functions 1", key="caf1"):
        next_state("State: Perform Aggregation 1")

if ss.state == "State: Perform Aggregation 1" or ("State: Perform Aggregation 1" in ss.state_list):

    st.subheader("state 5: Perform Aggregation")
    if st.button("Perform Aggregation 1", key="pa1"):
        next_state("State: Data Source 2")



#######################################################################
#######################################################################
#######################################################################
#######################################################################

if ss.state == "State: Data Source 2" or ("State: Data Source 2" in ss.state_list):
    
    st.subheader("state 5: Select Data Source")
    if st.button("Next Step",key="SDS2"):
        next_state("State: Load Data 2")

if ss.state == "State: Load Data 2" or ("State: Load Data 2" in ss.state_list):
    
    st.subheader("state 6: Load Data")
    next_state("State: Apply NaN Threshold 2")
    

if ss.state == "State: Apply NaN Threshold 2" or ("State: Apply NaN Threshold 2" in ss.state_list):
    
    st.subheader("state 7: Apply NaN Threshold")
    if st.button("Apply Threshold 2", key="at2"):
        next_state("State: Select Columns of Interest 2")

if ss.state == "State: Select Columns of Interest 2" or ("State: Select Columns of Interest 2" in ss.state_list):
    
    st.subheader("state 8: Select Columns of Interest")
    if st.button("Confirm Column Selection 2", key="ccs2"):
        next_state("State: Select Aggregation Functions 2")

if ss.state == "State: Select Aggregation Functions 2" or ("State: Select Aggregation Functions 2" in ss.state_list):
    
    st.subheader("state 9: Select Aggregation Functions")
    if st.button("Confirm Aggregation Functions 2", key="caf2"):
        next_state("State: Perform Aggregation 2")

if ss.state == "State: Perform Aggregation 2" or ("State: Perform Aggregation 2" in ss.state_list):
    
    st.subheader("state 10: Perform Aggregation")
    if st.button("Perform Aggregation 1", key="pa2"):
        st.write(ss.agg_df_2)
        next_state("State: Merge Datasets")
        

# Merge Datasets
if ss.state == "State: Merge Datasets" or ("State: Merge Datasets" in ss.state_list):
    
    st.header("Merge Datasets")

    st.subheader("Start Over")
    if st.button("Reset", key="reset"):
        for key in list(ss.keys()):
            del ss[key]
        ss.state = "State: Data Source 1"
        ss.state_list = ["State: Data Source 1"]

