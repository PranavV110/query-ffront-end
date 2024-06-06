import streamlit as st
import pandas as pd
import datetime

# Function to load CSV data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# Streamlit app interface
st.sidebar.title("Select Search Parameters")

# Specify the path to your CSV file
csv_file_path = r"updated_papers_op.csv"

# Load data
data = load_data(csv_file_path)

# Preprocess date column to convert it into a consistent format
def preprocess_date(date_str):
    try:
        return pd.to_datetime(date_str)
    except ValueError:
        return pd.NaT  # Return NaT (Not a Time) for invalid date strings

data['publication_date'] = data['publication_date'].apply(preprocess_date)

# Filter out rows with NaT (invalid date strings)
data = data.dropna(subset=['publication_date'])

# Exclude papers before the year 1990
data = data[data['publication_date'].dt.year >= 1990]

# Get min and max dates from the dataframe
min_date = data['publication_date'].min()
max_date = data['publication_date'].max()

# Pre-selected date range
yearmin = min_date.year
yearmax = max_date.year

# Date range slider by year
dates_selection = st.sidebar.slider("Select year range:",
                                    min_value=yearmin,
                                    max_value=yearmax,
                                    value=(yearmin, yearmax),
                                    step=1)

# Get unique keywords from the dataset (using "title" column for suggestions)
unique_keywords = data['title'].dropna().unique().tolist()

# Keyword search with real-time suggestions
selected_keywords = st.sidebar.multiselect("Select keywords:", unique_keywords)

# Get unique data sources from the dataset
data_sources = data['data_source'].dropna().unique().tolist()

# Get unique types from the dataset
unique_types = data['type'].dropna().unique().tolist()

# Author search with real-time suggestions
unique_authors = data['full_name'].dropna().unique().tolist()
selected_authors = st.sidebar.multiselect("Select authors:", unique_authors)

# Sidebar checkboxes for data sources
selected_sources = []
st.sidebar.write("Select Source(s):")
for source in data_sources:
    if st.sidebar.checkbox(source, key=f'source_{source}'):
        selected_sources.append(source)

# Sidebar checkboxes for types
selected_types = []
st.sidebar.write("Select Type(s):")
for t in unique_types:
    if st.sidebar.checkbox(t, key=f'type_{t}'):
        selected_types.append(t)

# Display filtered data
st.title("Advanced Search")
filtered_data = data[(data['publication_date'].dt.year >= dates_selection[0]) & 
                     (data['publication_date'].dt.year <= dates_selection[1])]

if selected_keywords:
    mask = filtered_data['title'].apply(lambda x: any(keyword in x for keyword in selected_keywords))
    filtered_data = filtered_data[mask]

if selected_authors:
    mask = filtered_data['full_name'].apply(lambda x: any(author in x for author in selected_authors))
    filtered_data = filtered_data[mask]

if selected_sources:
    filtered_data = filtered_data[filtered_data['data_source'].isin(selected_sources)]

if selected_types:
    filtered_data = filtered_data[filtered_data['type'].isin(selected_types)]

st.write(filtered_data[["title", "full_name", "publication_date", "publication", "data_source", "type"]])
