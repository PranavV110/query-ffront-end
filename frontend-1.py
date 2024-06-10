import streamlit as st
import pandas as pd
import datetime

# Function to load CSV data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')
    df = df.dropna(subset=['publication_date'])
    df = df[df['publication_date'].dt.year >= 1990]
    return df

# Streamlit app interface
st.sidebar.title("Enter Search Parameters")

# Specify the path to your CSV file
csv_file_path = "updated_papers_op.csv"

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

# Date range selection with default current date
st.sidebar.write("Select date range:")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start date", value=current_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("End date", value=current_date, min_value=min_date, max_value=max_date)

# Keyword search input field
keyword = st.sidebar.text_input("Enter a keyword to search in the entire DataFrame:")

# Checkboxes for data sources
st.sidebar.write("Select Source(s):")
data_sources = [source.strip() for source in data['data_source'].dropna().unique().tolist() if source.strip()]
selected_sources = [source for source in data_sources if st.sidebar.checkbox(source, key=f'source_{source}')]

# Checkboxes for types
st.sidebar.write("Select Type(s):")
unique_types = [t.strip() for t in data['type'].dropna().unique().tolist() if t.strip()]
selected_types_checkboxes = [t for t in unique_types if st.sidebar.checkbox(t, key=f'type_{t}')]

# Search button
if st.sidebar.button("Search"):
    # Perform filtering
    mask = (data['publication_date'] >= pd.Timestamp(start_date)) & (data['publication_date'] <= pd.Timestamp(end_date))

    if keyword:
        keyword = keyword.lower()
        mask &= data.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)

    if selected_sources:
        mask &= data['data_source'].isin(selected_sources)

    if selected_types_checkboxes:
        mask &= data['type'].isin(selected_types_checkboxes)

    filtered_data = data[mask]

    # Store results in session state
    st.session_state['filtered_data'] = filtered_data

# Function to create a hyperlink
def make_clickable(link):
    return f'<a href="{link}" target="_blank">{link}</a>'

# Pagination
def paginate_data(data, page, page_size):
    return data.iloc[page * page_size:(page + 1) * page_size]

# Display filtered data
st.title("Filtered Results")
if 'filtered_data' in st.session_state:
    filtered_data = st.session_state['filtered_data'].copy()
    
    # Make link column clickable
    filtered_data['link'] = filtered_data['link'].apply(lambda x: make_clickable(x) if pd.notna(x) else '')
    
    # Pagination controls
    page_size = 10
    total_pages = len(filtered_data) // page_size + 1
    page = st.number_input("Page", 0, total_pages - 1, 0)
    
    paginated_data = paginate_data(filtered_data, page, page_size)
    
    # Convert the DataFrame to HTML and style it
    filtered_data_html = paginated_data[["title", "full_name", "publication_date", "publication", "data_source", "type", "link"]].to_html(index=False, escape=False)
    
    # Render the HTML using st.markdown to ensure links are clickable
    st.markdown(
        """
        <style>
        .reportview-container .main .block-container{
            padding-top: 20px;
            padding-right: 20px;
            padding-left: 20px;
            padding-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
        }
        a {
            color: #1f77b4;
            text-decoration: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown(filtered_data_html, unsafe_allow_html=True)
else:
    st.write("Please set your filters and press 'Search' to see the results.")
