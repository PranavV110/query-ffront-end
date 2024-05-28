import streamlit as st
import pandas as pd

# Function to load CSV data
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    return df

# Function to calculate percentage of True/False values
def calculate_percentage(series):
    total = len(series)
    true_count = series.sum()
    false_count = total - true_count
    true_percentage = (true_count / total) * 100
    false_percentage = (false_count / total) * 100
    return true_percentage, false_percentage

# Streamlit app interface
st.title("CSV Groupby and Statistics App")

# Upload CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Load data
    data = load_data(uploaded_file)

    # Display data
    st.header("Data Preview")
    st.write(data.head())

    # Select column to group by
    groupby_column = st.selectbox("Select column to group by", data.columns)

    # Select column(s) for aggregation
    agg_columns = st.multiselect("Select column(s) for aggregation", data.columns)

    # Select aggregation function(s)
    agg_func_options = ["mean", "sum", "count", "min", "max"]
    agg_functions = st.multiselect("Select aggregation function(s)", agg_func_options)

    # Select column for percentage calculation
    percentage_column = st.selectbox("Select column for True/False percentage calculation", data.columns)

    if st.button("Generate Statistics"):
        if agg_columns and agg_functions:
            # Create a dictionary for aggregations
            agg_dict = {col: agg_functions for col in agg_columns}
            
            # Perform groupby and aggregation
            grouped_data = data.groupby(groupby_column).agg(agg_dict)
            st.header("Groupby Statistics")
            st.write(grouped_data)
        else:
            st.error("Please select at least one column and one aggregation function.")
        
        # Calculate and display percentage of True/False values
        if percentage_column:
            if data[percentage_column].dtype == bool:
                true_percentage, false_percentage = calculate_percentage(data[percentage_column])
                st.header("Percentage of True/False Values")
                st.write(f"True: {true_percentage:.2f}%")
                st.write(f"False: {false_percentage:.2f}%")
            else:
                st.error("The selected column is not of boolean type.")
else:
    st.info("Please upload a CSV file to proceed.")
