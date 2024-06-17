import streamlit as st
import pandas as pd
import datetime
from fuzzywuzzy import fuzz, process

# Function to load CSV data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')
    #df = df.dropna(subset=['publication_date'])
    df = df[df['publication_date'].dt.year >= 1990]
    return df

# Function to convert DataFrame to CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Function to create a hyperlink
def make_clickable(link):
    return f'<a href="{link}" target="_blank">{link}</a>'

# Fuzzy matching function
def fuzzy_match(query, choices, score_cutoff=70):
    results = process.extract(query, choices, scorer=fuzz.token_set_ratio)
    return [match for match, score in results if score >= score_cutoff]

# Pagination function
def paginate_data(data, page, page_size):
    return data.iloc[page * page_size:(page + 1) * page_size]

# Streamlit app interface
st.sidebar.title("Enter Search Parameters")

# Specify the path to your CSV file
csv_file_path = "updated_papers_op.csv"

# Load data
data = load_data(csv_file_path)

data = data[data['data_source'] != 'dblp']

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

# Ensure the default start date is within the valid range
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

# Checkboxes for data sources
st.sidebar.write("Select Source(s):")
data_sources = [source.strip() for source in data['data_source'].dropna().unique().tolist() if source.strip()]
selected_sources = [source for source in data_sources if st.sidebar.checkbox(source, key=f'source_{source}')]

# Checkboxes for types
st.sidebar.write("Select Type(s):")
unique_types = [t.strip() for t in data['type'].dropna().unique().tolist() if t.strip()]
selected_types_checkboxes = [t for t in unique_types if st.sidebar.checkbox(t, key=f'type_{t}')]

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state['page'] = 0

# Search button
if st.sidebar.button("Search"):
    with st.spinner('Filtering data...'):
        # Perform filtering
        mask = (data['publication_date'] >= pd.Timestamp(start_date)) & (data['publication_date'] <= pd.Timestamp(end_date))
        st.write(f"Date range filter: {mask.sum()} rows matched")
        
        if title_keyword:
            title_keyword = title_keyword.lower()
            matched_titles = fuzzy_match(title_keyword, data['title'].astype(str).tolist())
            mask &= data['title'].isin(matched_titles)
            st.write(f"Title keyword filter: {len(matched_titles)} matches found, {mask.sum()} rows matched")

        if author_keyword:
            author_keyword = author_keyword.lower()
            matched_authors = fuzzy_match(author_keyword, data['full_name'].astype(str).tolist())
            mask &= data['full_name'].isin(matched_authors)
            st.write(f"Author keyword filter: {len(matched_authors)} matches found, {mask.sum()} rows matched")

        if selected_sources:
            mask &= data['data_source'].isin(selected_sources)
            st.write(f"Source filter: {len(selected_sources)} selected, {mask.sum()} rows matched")

        if selected_types_checkboxes:
            mask &= data['type'].isin(selected_types_checkboxes)
            st.write(f"Type filter: {len(selected_types_checkboxes)} selected, {mask.sum()} rows matched")

        filtered_data = data[mask]
        st.write(f"Total filtered rows: {len(filtered_data)}")

        # Store results in session state
        st.session_state['filtered_data'] = filtered_data
        st.session_state['page'] = 0  # Reset to the first page

# Display title
st.markdown("<h1 style='text-align: center;'>Filtered Results</h1>", unsafe_allow_html=True)

# Display filtered data
if 'filtered_data' in st.session_state:
    filtered_data = st.session_state['filtered_data'].copy()

    # Make link column clickable
    filtered_data['link'] = filtered_data['link'].apply(lambda x: make_clickable(x) if pd.notna(x) else '')

    # Clean up special characters in the DataFrame
    filtered_data.replace({r'\n': ' ', r'\r': ' '}, regex=True, inplace=True)

    # Pagination controls
    page_size = 100
    total_pages = (len(filtered_data) + page_size - 1) // page_size  # Compute total pages
    page = st.session_state['page']

    paginated_data = paginate_data(filtered_data, page, page_size)

    # Convert the DataFrame to HTML and style it
    filtered_data_html = paginated_data[["full_name", "title", "publication_date", "data_source", "type", "link"]].to_html(index=False, escape=False)

    # Apply CSS to prioritize width for 'title' and 'full_name' columns and limit row height
    st.markdown("""
        <style>
        .dataframe {
            width: 100%;
            table-layout: auto;
            overflow-x: auto;
            margin-left: -165px; /* Shift table slightly to the left */
        }
        .dataframe th, .dataframe td {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 300px;
            max-height: 2.4em;
            line-height: 1.2em;
            padding: 0.6em;
        }
        .dataframe td:nth-child(1), .dataframe td:nth-child(2) {
            max-width: 250px;
        }
        .dataframe td:nth-child(5) {
            max-width: 150px;
        }
        </style>
        """, unsafe_allow_html=True)

    # Render the HTML using st.markdown to ensure links are clickable
    st.markdown(filtered_data_html, unsafe_allow_html=True)

    # Display number of results on the current page and total number of filtered results
    current_page_results = len(paginated_data)
    total_results = len(filtered_data)
    st.subheader(f"Showing {current_page_results} of {total_results} results")

    # Convert filtered data to CSV
    csv = convert_df_to_csv(filtered_data)

    # Download button on the sidebar
    st.sidebar.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv',
    )

    # Pagination controls
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Previous"):
            if st.session_state['page'] > 0:
                st.session_state['page'] -= 1
    with col2:
        if st.button("Next"):
            if st.session_state['page'] < total_pages - 1:
                st.session_state['page'] += 1

else:
    st.write("Please set your filters and press 'Search' to see the results.")
