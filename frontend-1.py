import streamlit as st
import pandas as pd

# Function to load CSV data
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    return df

# Streamlit app interface
st.title("CSV Value Filter App")

# Upload CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Load data
    data = load_data(uploaded_file)

    # Display data
    st.header("Data Preview")
    st.write(data.head())

    # Input for keyword search
    keyword = st.text_input("Enter a keyword to search for:")

    if keyword:
        # Filter data based on keyword
        data = data[data.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]

    # Display filters for each column
    st.header("Filters")
    filters = {}
    for column in data.columns:
        unique_values = data[column].unique()
        selected_values = st.multiselect(f"Filter values for {column}", unique_values, default=unique_values)
        filters[column] = selected_values

    # Apply filters
    for column, selected_values in filters.items():
        data = data[data[column].isin(selected_values)]

    # Display filtered data
    st.header(f"Filtered Data (Keyword: {keyword})")
    st.write(data)
else:
    st.info("Please upload a CSV file to proceed.")
