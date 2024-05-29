import streamlit as st
import pandas as pd

# Function to load CSV data
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df = df.drop_na(subset=['pdf_link'])
    return df

# Function to calculate breakdown of each value in a column
def calculate_breakdown(data):
    breakdown = {}
    for column in data.columns:
        value_counts = data[column].value_counts()
        percentages = data[column].value_counts(normalize=True) * 100
        breakdown[column] = pd.DataFrame({'Count': value_counts, 'Percentage': percentages})
    return breakdown

# Streamlit app interface
st.title("CSV Value Breakdown App")

# Upload CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Load data
    data = load_data(uploaded_file)

    # Display data
    st.header("Data Preview")
    st.write(data.head())

    # Calculate and display breakdown of each value in every column
    st.header("Breakdown of Each Value per Column")
    breakdown = calculate_breakdown(data)
    for column, breakdown_df in breakdown.items():
        st.subheader(f"Column: {column}")
        st.write(breakdown_df)
else:
    st.info("Please upload a CSV file to proceed.")
