import streamlit as st
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

def suggest_column_matches(source_cols, target_cols, threshold=0.6):
    """Suggest matching columns based on name similarity"""
    matches = {}
    for s_col in source_cols:
        scores = [(t_col, SequenceMatcher(None, s_col.lower(), t_col.lower()).ratio()) 
                 for t_col in target_cols]
        best_match = max(scores, key=lambda x: x[1])
        if best_match[1] >= threshold:
            matches[s_col] = best_match[0]
    return matches

def analyze_column_relationship(series1, series2):
    """Analyze potential relationship between columns"""
    try:
        if pd.api.types.is_numeric_dtype(series1) and pd.api.types.is_numeric_dtype(series2):
            valid_mask = ~(series1.isna() | series2.isna())
            if valid_mask.sum() > 1:  # Need at least 2 points for correlation
                return series1[valid_mask].corr(series2[valid_mask])
    except Exception as e:
        print(f"Error calculating correlation: {e}")
    return None

def analyze_column_types(df1, df2, col1, col2):
    """Analyze compatibility between two columns"""
    type1 = df1[col1].dtype
    type2 = df2[col2].dtype
    compatible = type1 == type2
    
    correlation = analyze_column_relationship(df1[col1], df2[col2])
    
    details = {
        "type1": str(type1),
        "type2": str(type2),
        "compatible": compatible,
        "unique_values1": df1[col1].nunique(),
        "unique_values2": df2[col2].nunique(),
        "null_pct1": (df1[col1].isna().sum() / len(df1)) * 100,
        "null_pct2": (df2[col2].isna().sum() / len(df2)) * 100,
        "correlation": correlation
    }
    return details

def plot_column_evolution(evolution_graph):
    """Plot column evolution diagram using networkx"""
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(evolution_graph)
    nx.draw(evolution_graph, pos, with_labels=True, node_color='lightblue', 
            node_size=2000, font_size=8, font_weight='bold', arrows=True)
    plt.title("Column Evolution Over Time")
    return plt

def initialize_column_tracking():
    """Initialize column tracking in session state"""
    if 'column_evolution' not in st.session_state:
        st.session_state.column_evolution = {
            'graph': nx.DiGraph(),
            'history': [],
            'bifurcations': {},
            'new_columns': {}
        }

st.set_page_config(page_title="Add Records", page_icon="📝", layout="wide")
initialize_column_tracking()

st.title("Add Records 📝")

if not st.session_state.Data_Bases:
    st.warning("No data loaded. Please load and filter data first.")
else:
    st.subheader("Stack Datasets with Column Evolution Tracking")
    
    # Select datasets
    col1, col2 = st.columns(2)
    with col1:
        base_idx = st.selectbox(
            "Select base dataset",
            range(len(st.session_state.Data_Bases)),
            format_func=lambda x: f"Database {x+1}"
        )
    with col2:
        stack_idx = st.selectbox(
            "Select dataset to stack",
            [i for i in range(len(st.session_state.Data_Bases)) if i != base_idx],
            format_func=lambda x: f"Database {x+1}"
        )
    
    if base_idx != stack_idx:
        base_df = st.session_state.Data_Bases[base_idx]
        stack_df = st.session_state.Data_Bases[stack_idx]
        
        # Column Evolution Tracking
        st.subheader("Column Evolution")
        
        # Track new columns
        new_columns = set(stack_df.columns) - set(base_df.columns)
        if new_columns:
            st.info(f"New columns detected: {', '.join(new_columns)}")
            for col in new_columns:
                st.session_state.column_evolution['new_columns'][col] = {
                    'first_appearance': datetime.now(),
                    'source_dataset': f"Database {stack_idx + 1}"
                }
        
        # Column Bifurcation Interface
        st.subheader("Column Bifurcation")
        
        # Allow users to specify column bifurcations
        bifurcate = st.checkbox("Does any column split into multiple columns?")
        if bifurcate:
            source_col = st.selectbox("Select source column", base_df.columns)
            target_cols = st.multiselect("Select resulting columns", stack_df.columns)
            
            if source_col and target_cols:
                if st.button("Confirm Bifurcation"):
                    # Record bifurcation in session state
                    st.session_state.column_evolution['bifurcations'][source_col] = {
                        'target_columns': target_cols,
                        'timestamp': datetime.now(),
                        'source_dataset': f"Database {base_idx + 1}",
                        'target_dataset': f"Database {stack_idx + 1}"
                    }
                    
                    # Update evolution graph
                    graph = st.session_state.column_evolution['graph']
                    for target in target_cols:
                        graph.add_edge(source_col, target)
                    
                    st.success("Bifurcation recorded!")
        
        # Column Mapping Interface
        st.subheader("Column Mapping")
        suggested_matches = suggest_column_matches(stack_df.columns, base_df.columns)
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Column Mapper", "Column Analysis", "Evolution Visualization"])
        
        with tab1:
            col_map = {}
            for stack_col in stack_df.columns:
                suggested = suggested_matches.get(stack_col, "")
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"**{stack_col}**")
                with col2:
                    selected = st.selectbox(
                        f"Map to base column",
                        [""] + list(base_df.columns),
                        index=0 if not suggested else list(base_df.columns).index(suggested) + 1,
                        key=f"map_{stack_col}"
                    )
                    if selected:
                        col_map[stack_col] = selected
                with col3:
                    if selected:
                        compatibility = analyze_column_types(base_df, stack_df, selected, stack_col)
                        if compatibility["compatible"]:
                            st.success("✓ Compatible")
                        else:
                            st.warning("⚠ Type mismatch")
        
        with tab2:
            if col_map:
                for stack_col, base_col in col_map.items():
                    with st.expander(f"Analysis: {stack_col} → {base_col}"):
                        analysis = analyze_column_types(base_df, stack_df, base_col, stack_col)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Base Column**")
                            st.markdown(f"Type: {analysis['type1']}")
                            st.markdown(f"Unique Values: {analysis['unique_values1']}")
                            st.markdown(f"Null %: {analysis['null_pct1']:.2f}%")
                        with col2:
                            st.markdown("**Stack Column**")
                            st.markdown(f"Type: {analysis['type2']}")
                            st.markdown(f"Unique Values: {analysis['unique_values2']}")
                            st.markdown(f"Null %: {analysis['null_pct2']:.2f}%")
                        
                        if analysis['correlation'] is not None:
                            st.markdown(f"**Correlation**: {analysis['correlation']:.2f}")
                            if abs(analysis['correlation']) > 0.7:
                                st.success("Strong correlation")
                            elif abs(analysis['correlation']) > 0.4:
                                st.warning("Moderate correlation")
                            else:
                                st.error("Weak correlation")
                        else:
                            st.info("Correlation not applicable (non-numeric data)")
        
        with tab3:
            # Visualize column evolution
            if st.session_state.column_evolution['graph'].number_of_edges() > 0:
                fig = plot_column_evolution(st.session_state.column_evolution['graph'])
                st.pyplot(fig)
                
                # Show bifurcation history
                st.subheader("Bifurcation History")
                for source, info in st.session_state.column_evolution['bifurcations'].items():
                    st.markdown(f"""
                    - Source column '{source}' from {info['source_dataset']} split into:
                      {', '.join(info['target_columns'])} in {info['target_dataset']}
                    """)
            else:
                st.info("No column evolution recorded yet.")
        
        # Stacking Interface
        st.subheader("Stack Datasets")
        
        # Add timestamp/version identifier
        add_identifier = st.checkbox("Add timestamp/version identifier")
        if add_identifier:
            base_date = st.date_input("Date for Base Dataset")
            stack_date = st.date_input("Date for Stack Dataset")
            
        if st.button("Preview Stacking") and col_map:
            try:
                # Prepare dataframes for stacking
                base_subset = base_df.copy()
                stack_subset = stack_df.copy()
                
                # Handle bifurcated columns
                for source_col, bifurcation in st.session_state.column_evolution['bifurcations'].items():
                    if source_col in base_subset.columns:
                        # Fill NaN for bifurcated columns in base dataset
                        for target_col in bifurcation['target_columns']:
                            base_subset[target_col] = np.nan
                
                # Handle new columns
                for new_col in new_columns:
                    if new_col not in base_subset.columns:
                        base_subset[new_col] = np.nan
                
                # Add identifier if selected
                if add_identifier:
                    base_subset['timestamp'] = base_date
                    stack_subset['timestamp'] = stack_date
                
                # Stack datasets
                stacked_df = pd.concat([base_subset, stack_subset], axis=0, ignore_index=True)
                
                # Show preview
                st.subheader("Preview of Stacked Dataset")
                st.write(stacked_df.head())
                
                # Show statistics
                st.subheader("Stacking Statistics")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Records", len(stacked_df))
                    st.metric("Total Columns", len(stacked_df.columns))
                with col2:
                    st.metric("New Columns", len(new_columns))
                    st.metric("Bifurcated Columns", len(st.session_state.column_evolution['bifurcations']))
                
                # Confirm stacking
                if st.button("Confirm and Stack Datasets"):
                    st.session_state.Data_Bases.append(stacked_df)
                    st.success("Datasets stacked successfully!")
                    st.rerun()
                
            except Exception as e:
                st.error(f"Error stacking datasets: {str(e)}")
                st.write("Please check your column mappings and try again.")

    # Option to remove the last added database
    if len(st.session_state.Data_Bases) > 0:
        if st.button("Remove Last Added Database"):
            st.session_state.Data_Bases.pop()
            st.success("Last database removed successfully!")
            st.rerun()