import streamlit as st
import pandas as pd

# Function to load CSV data
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    return df

# Streamlit app interface
st.title("CSV Keyword Search App")

# Upload CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Load data
    data = load_data(uploaded_file)

    # Input for keyword search
    keyword = st.text_input("Enter a keyword to search for:")

    if keyword:
        # Filter data based on keyword
        filtered_data = data[data.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]
        
        # Display filtered data
        st.header(f"Filtered Data (Keyword: {keyword})")
        st.write(filtered_data)
    else:
        st.header("Data Preview")
        st.write(data.head())
else:
    st.info("Please upload a CSV file to proceed.")
