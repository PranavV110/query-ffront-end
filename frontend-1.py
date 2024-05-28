import streamlit as st
import pandas as pd

# Function to load CSV data
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    return df

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
    agg_column = st.multiselect("Select column(s) for aggregation", data.columns)

    # Select aggregation function
    agg_func = st.selectbox("Select aggregation function", ["mean", "sum", "count", "min", "max"])

    if st.button("Generate Statistics"):
        if agg_column:
            # Perform groupby and aggregation
            grouped_data = data.groupby(groupby_column)[agg_column].agg(agg_func)
            st.header("Groupby Statistics")
            st.write(grouped_data)
        else:
            st.error("Please select at least one column for aggregation.")
else:
    st.info("Please upload a CSV file to proceed.")
