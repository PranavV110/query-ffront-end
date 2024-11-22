import streamlit as st
import pandas as pd
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Function to load CSV data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['publication_date'] = pd.to_datetime(df['publication_date'], format='mixed', errors='coerce')
    df.fillna('N/A', inplace=True)
    return df

# Function to convert DataFrame to CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Function to create a hyperlink for the title
def make_clickable(title, link):
    if pd.notna(link):
        return f'<a href="{link}" target="_blank">{title}</a>'
    return title  # Return just the title if link is not available

# Function to find similar entries using cosine similarity for any column (titles/authors)
def find_similar_entries(query, column_data):
    vectorizer = TfidfVectorizer(stop_words='english')
    column_vectors = vectorizer.fit_transform(column_data)
    query_vector = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vector, column_vectors).flatten()
    similar_indices = cosine_similarities.argsort()[::-1]
    similar_entries = [column_data.iloc[i] for i in similar_indices if cosine_similarities[i] > 0.1]
    return similar_entries

# Function to find the best match in a list of authors
def find_best_match_in_authors(query, authors_list):
    vectorizer = TfidfVectorizer(stop_words='english')
    all_authors = [author.strip() for authors in authors_list for author in authors.split(',')]
    all_authors = list(set(all_authors))  # Deduplicate author names
    if not all_authors:
        return "N/A"
    author_vectors = vectorizer.fit_transform(all_authors)
    query_vector = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vector, author_vectors).flatten()
    best_match_idx = cosine_similarities.argmax()
    if cosine_similarities[best_match_idx] > 0.1:
        return all_authors[best_match_idx]
    return "No match"

# Pagination function
def paginate_data(data, page, page_size):
    return data.iloc[page * page_size:(page + 1) * page_size]

# Streamlit app interface
st.sidebar.title("Enter Search Parameters")

# Specify the path to your CSV file
csv_file_path = "combined_schema.csv"

# Load data
data = load_data(csv_file_path)

# Get min and max dates from the dataframe
min_date = data['publication_date'].min().date()
max_date = data['publication_date'].max().date()

# Set current date within the valid range
current_date = datetime.date.today()
if current_date < min_date:
    current_date = min_date
if current_date > max_date:
    current_date = max_date

# Set default end date to current date and start date to one year before
default_end_date = current_date
default_start_date = current_date - datetime.timedelta(days=365)
if default_start_date < min_date:
    default_start_date = min_date

# Date range selection with default current date
st.sidebar.write("Select date range:")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start date", value=default_start_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("End date", value=default_end_date, min_value=min_date, max_value=max_date)

# Keyword search input fields
title_keyword = st.sidebar.text_input("Enter a keyword to search in titles:")
author_keyword = st.sidebar.text_input("Enter a keyword to search in author names:")

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state['page'] = 0

# Search button
if st.sidebar.button("Search"):
    with st.spinner('Filtering data...'):
        data['publication_date'] = pd.to_datetime(data['publication_date'], errors='coerce')
        mask = (data['publication_date'] >= pd.Timestamp(start_date)) & (data['publication_date'] <= pd.Timestamp(end_date))
        
        if title_keyword:
            similar_titles = find_similar_entries(title_keyword, data['title'])
            mask &= data['title'].isin(similar_titles)

        if author_keyword:
            data['best_match_author'] = data['authors'].apply(lambda x: find_best_match_in_authors(author_keyword, [x]))
            mask &= data['best_match_author'] != "No match"

        filtered_data = data[mask]
        st.session_state['filtered_data'] = filtered_data
        st.session_state['page'] = 0

# Display title
st.markdown("<h1 style='text-align: center;'>Filtered Results</h1>", unsafe_allow_html=True)

# Display filtered data
if 'filtered_data' in st.session_state:
    filtered_data = st.session_state['filtered_data'].copy()
    filtered_data['title'] = filtered_data.apply(lambda x: make_clickable(x['title'], x['link']), axis=1)
    filtered_data.replace({r'\n': ' ', r'\r': ' '}, regex=True, inplace=True)
    filtered_data = filtered_data.astype(str)

    page_size = 100
    total_pages = (len(filtered_data) + page_size - 1) // page_size
    page = st.session_state['page']

    paginated_data = paginate_data(filtered_data, page, page_size)
    #paginated_data = paginated_data.drop(columns=['link', 'authors'])
    paginated_data.rename(columns={'best_match_author': 'author'}, inplace=True)
    
    filtered_data_html = paginated_data[["authors", "title", "publication_date"]].to_html(index=False, escape=False)
    st.markdown(filtered_data_html, unsafe_allow_html=True)

    current_page_results = len(paginated_data)
    total_results = len(filtered_data)
    start_idx = page * page_size + 1
    end_idx = start_idx + current_page_results - 1
    st.subheader(f"Showing {start_idx}-{end_idx} of {total_results} results")

    csv = convert_df_to_csv(filtered_data)
    st.sidebar.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv',
    )

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
