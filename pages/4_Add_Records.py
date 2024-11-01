import streamlit as st
import pandas as pd
from instructions import INSTRUCTIONS

st.set_page_config(page_title="Add Records", page_icon="📝")

st.title("Add Records 📝")

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown(INSTRUCTIONS["add_records"])

if not st.session_state.Data_Bases:
    st.warning("No data loaded. Please load and filter data first.")
else:
    st.subheader("Stack Similar Datasets")
    
    # Multi-select for databases
    db_indices = st.multiselect(
        "Select databases to stack (must have similar structure)",
        range(len(st.session_state.Data_Bases)),
        format_func=lambda x: f"Database {x+1}"
    )
    
    if db_indices:
        # Get selected dataframes
        selected_dfs = [st.session_state.Data_Bases[i] for i in db_indices]
        
        # Show column comparison
        st.subheader("Column Comparison")
        comparison_df = pd.DataFrame({
            f"DB_{i+1}_columns": df.columns.tolist() 
            for i, df in enumerate(selected_dfs)
        })
        st.dataframe(comparison_df)
        
        # Select columns to stack
        common_columns = list(set.intersection(*[set(df.columns) for df in selected_dfs]))
        selected_columns = st.multiselect(
            "Select columns to include in stacked dataset",
            common_columns,
            default=common_columns
        )
        
        # Option to add date/identifier column
        add_identifier = st.checkbox("Add source identifier column")
        if add_identifier:
            identifier_type = st.radio(
                "Choose identifier type",
                ["Automatic Index", "Custom Labels", "Date Values"]
            )
            
            if identifier_type == "Custom Labels":
                identifiers = [
                    st.text_input(f"Label for Database {i+1}", value=f"Source_{i+1}")
                    for i in db_indices
                ]
            elif identifier_type == "Date Values":
                identifiers = [
                    st.date_input(f"Date for Database {i+1}")
                    for i in db_indices
                ]
            else:
                identifiers = [f"DB_{i+1}" for i in db_indices]

        if st.button("Stack Datasets"):
            try:
                # Filter selected columns
                filtered_dfs = [df[selected_columns] for df in selected_dfs]
                
                # Add identifier column if selected
                if add_identifier:
                    for i, df in enumerate(filtered_dfs):
                        df['source'] = identifiers[i]
                
                # Stack dataframes
                stacked_df = pd.concat(filtered_dfs, axis=0, ignore_index=True)
                
                # Add to session state
                st.session_state.Data_Bases.append(stacked_df)
                
                # Show results
                st.success("Datasets stacked successfully!")
                st.subheader("Preview of Stacked Dataset")
                st.write(stacked_df.head())
                
                # Show statistics
                st.subheader("Stacking Statistics")
                stats_col1, stats_col2 = st.columns(2)
                with stats_col1:
                    st.metric("Total Records", len(stacked_df))
                    st.metric("Total Columns", len(stacked_df.columns))
                with stats_col2:
                    if add_identifier:
                        st.metric("Number of Sources", len(identifiers))
                        source_counts = stacked_df['source'].value_counts()
                        st.write("Records per source:")
                        st.write(source_counts)
                
            except Exception as e:
                st.error(f"Error stacking datasets: {str(e)}")
                st.write("Please make sure the selected columns are compatible across all datasets.")

    # Option to remove the last added database
    if len(st.session_state.Data_Bases) > 0:
        if st.button("Remove Last Added Database"):
            st.session_state.Data_Bases.pop()
            st.success("Last database removed successfully!")
            st.rerun()