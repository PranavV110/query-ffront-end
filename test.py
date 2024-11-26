import streamlit as st
import pandas as pd
import joblib
import os
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Function to compute TF-IDF vectors and save them as a .pkl file
def compute_and_save_tfidf(data, pkl_file_path):
    with st.spinner("Precomputing TF-IDF vectors..."):
        # Compute TF-IDF for titles
        title_vectorizer = TfidfVectorizer(stop_words="english")
        title_vectors = title_vectorizer.fit_transform(data["title"].fillna(""))

        # Compute TF-IDF for authors
        author_vectorizer = TfidfVectorizer(stop_words="english")
        author_vectors = author_vectorizer.fit_transform(data["authors"].fillna(""))

        # Save everything into a .pkl file
        data_dict = {
            "data": data,
            "title_vectorizer": title_vectorizer,
            "title_vectors": title_vectors,
            "author_vectorizer": author_vectorizer,
            "author_vectors": author_vectors,
        }
        with open(pkl_file_path, "wb") as f:
            joblib.dump(data_dict, f)
        st.success("TF-IDF vectors precomputed and saved!")

# Function to load precomputed data from the .pkl file
@st.cache_resource
def load_precomputed_data(pkl_file_path):
    with open(pkl_file_path, "rb") as f:
        data_dict = joblib.load(f)
    return (
        data_dict["data"],
        data_dict["title_vectorizer"],
        data_dict["title_vectors"],
        data_dict["author_vectorizer"],
        data_dict["author_vectors"],
    )

# Function to find similar entries using precomputed TF-IDF vectors
def find_similar_entries(query, vectorizer, vectors):
    query_vector = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vector, vectors).flatten()
    similar_indices = cosine_similarities.argsort()[::-1]
    return similar_indices[cosine_similarities[similar_indices] > 0.1]

# Function to load CSV data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df["publication_date"] = pd.to_datetime(df["publication_date"], format="mixed", errors="coerce")
    df.fillna("N/A", inplace=True)
    return df

# Streamlit app interface
st.sidebar.title("Enter Search Parameters")

# CSV file path (replace with your file)
csv_file_path = "combined_schema.csv"
data = load_data(csv_file_path)

# Local .pkl file path
pkl_file_path = "tfidf_data.pkl"

# Check if the .pkl file exists, and create it if not
if not os.path.exists(pkl_file_path):
    compute_and_save_tfidf(data, pkl_file_path)

# Load the precomputed data
data, title_vectorizer, title_vectors, author_vectorizer, author_vectors = load_precomputed_data(pkl_file_path)

# Get min and max dates from the dataset
data['publication_date'] = pd.to_datetime(data['publication_date'], errors='coerce')
min_date = data['publication_date'].min().date()
max_date = data['publication_date'].max().date()

# Date range selection
st.sidebar.write("Select date range:")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)

# Keyword search inputs
title_keyword = st.sidebar.text_input("Enter a keyword to search in titles:")
author_keyword = st.sidebar.text_input("Enter a keyword to search in author names:")

# Pagination setup
if 'page' not in st.session_state:
    st.session_state['page'] = 0

# Search button
if st.sidebar.button("Search"):
    with st.spinner("Filtering data..."):
        mask = (data['publication_date'] >= pd.Timestamp(start_date)) & (data['publication_date'] <= pd.Timestamp(end_date))
        
        if title_keyword:
            similar_title_indices = find_similar_entries(title_keyword, title_vectorizer, title_vectors)
            mask &= data.index.isin(similar_title_indices)

        if author_keyword:
            similar_author_indices = find_similar_entries(author_keyword, author_vectorizer, author_vectors)
            mask &= data.index.isin(similar_author_indices)

        filtered_data = data[mask]
        st.session_state['filtered_data'] = filtered_data
        st.session_state['page'] = 0

# Display results
st.markdown("<h1 style='text-align: center;'>Filtered Results</h1>", unsafe_allow_html=True)
if 'filtered_data' in st.session_state:
    filtered_data = st.session_state['filtered_data'].copy()
    filtered_data.replace({r'\n': ' ', r'\r': ' '}, regex=True, inplace=True)
    filtered_data = filtered_data.astype(str)

    page_size = 100
    total_pages = (len(filtered_data) + page_size - 1) // page_size
    page = st.session_state['page']

    paginated_data = filtered_data.iloc[page * page_size:(page + 1) * page_size]
    st.write(paginated_data)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Previous"):
            if st.session_state['page'] > 0:
                st.session_state['page'] -= 1
                st.rerun()
    with col2:
        if st.button("Next"):
            if st.session_state['page'] < total_pages - 1:
                st.session_state['page'] += 1
                st.rerun()
else:
    st.write("Please set your filters and press 'Search' to see the results.")
