import requests
import pandas as pd
import time

def get_author_ids(name):
    """Get a list of author IDs and names by author name."""
    base_url = "https://api.openalex.org/authors"
    query = f"search={name}"
    url = f"{base_url}?{query}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get('results', [])
        return [(author['id'], author['display_name']) for author in results]
    else:
        print(f"Error retrieving authors: {response.status_code}")
        return []

def get_author_works(author_id):
    """Get a list of works for a given author ID."""
    url = f"https://api.openalex.org/works?filter=author.id:{author_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Error retrieving works for {author_id}: {response.status_code}")
        return []

def main():
    # Read names from a CSV file
    input_file = "combined_data.csv"  # Replace with your input file name
    names_df = pd.read_csv(input_file)
    names = names_df['Name'].tolist()  # Replace 'Name' with the actual column name

    author_results = []

    for name in names:
        print(f"Searching for authors matching '{name}'...")
        authors = get_author_ids(name)
        for author_id, author_name in authors:
            print(f"Found author: {author_name} (ID: {author_id})")
            works = get_author_works(author_id)
            for work in works:
                publication_date = work.get('publication_date', 'Unknown')
                external_ids = work.get('ids', {})
                author_results.append({
                    "Author Name": author_name,
                    "Author ID": author_id,
                    "Work Title": work['title'],
                    "Publication Date": publication_date,
                    "OpenAlex ID": external_ids.get('openalex', 'N/A'),
                    "DOI": external_ids.get('doi', 'N/A'),
                    "MAG ID": external_ids.get('mag', 'N/A')
                })
        time.sleep(10)  # To respect API rate limits

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(author_results)
    df.to_csv("author_works.csv", index=False)
    print("Results saved to 'author_works.csv'.")

if __name__ == "__main__":
    main()
