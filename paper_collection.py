import pandas as pd
import requests
import requests
import json
import time
import os
import pandas as pd
import os
import json




df = pd.read_csv("new_sem_sch_collection.csv")
#df = df[0:50]
df = df.drop_duplicates(subset='link')
df = df.drop_duplicates(subset='title')



sdf = df[df['data_source'] == 'Semantic Scholar']
#for idx, row in sdf.iterrows():
#   print(row['link'].split('/')[-1])

paper_ss_list = list(set([row['link'].split('/')[-1] for idx, row in sdf.iterrows()]))
len(paper_ss_list)

def fetch_paper_data(paper_ss_list, start_index=0):
    json_responses = load_progress('paper_data.json')[0]  # Load existing responses
    for idx in range(start_index, len(paper_ss_list)):
        value = paper_ss_list[idx]
        base_url = f'https://recommendpapers.xyz/api/lookup_paper?id={value}&fields=title,authors,citationCount,externalIds'
        while True:
            try:
                response = requests.get(base_url)
                response.raise_for_status()
                json_data = response.json()
                json_responses.append(json_data)
                print(f"Processed {idx}: {base_url}")
                store_json_responses(json_responses, 'paper_data.json') 
                time.sleep(1)# Save after each successful fetch
                break
            except requests.ConnectionError:
                print('Connection error, pausing for 30 minutes...')
                time.sleep(1800)
            except requests.HTTPError as e:
                print(f"HTTP error occurred: {e}")
                break
            except KeyboardInterrupt:
                print('Process interrupted by user.')
                return json_responses, idx
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break
    return json_responses, len(paper_ss_list)

def store_json_responses(json_responses, filename):
    with open(filename, 'w') as f:
        json.dump(json_responses, f, indent=2)
    print(f"Data saved to {filename}")

def load_progress(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return data, len(data)
    return [], 0

# Usage
#paper_ss_list = ['paper_id_1', 'paper_id_2', 'paper_id_3']  # Replace with actual IDs
progress, start_index = load_progress('paper_data.json')
results, next_index = fetch_paper_data(paper_ss_list, start_index=start_index)

print(f"Processed {next_index} out of {len(paper_ss_list)} papers")
print(results)




# Open and read the JSON file
with open('paper_data.json', 'r') as file:
    data = json.load(file)

# Print the data
print(data)




# Create output directory
output_dir = "output_csv"
os.makedirs(output_dir, exist_ok=True)

# DataFrames to store extracted data
papers_df = pd.DataFrame(columns=["paperId", "title", "citationCount"])
authors_df = pd.DataFrame(columns=["authorId", "name"])
paper_authors_df = pd.DataFrame(columns=["paperId", "authorId"])
external_ids_df = pd.DataFrame(columns=["paperId", "DBLP", "ArXiv", "DOI", "CorpusId", "MAG", "PubMed", "PubMedCentral", "ACL"])

# Process data and populate DataFrames
for responses_item in data:
    papers = responses_item.get('papers', [])

    if isinstance(papers, list):
        for paper in papers:
            if isinstance(paper, dict):
                # Extract paper information
                paper_id = paper.get('paperId')
                title = paper.get('title')
                citation_count = paper.get('citationCount')

                # Append to papers_df
                papers_df = pd.concat([papers_df, pd.DataFrame([{
                    "paperId": paper_id,
                    "title": title,
                    "citationCount": citation_count
                }])], ignore_index=True)

                # Extract external IDs
                external_ids = paper.get('externalIds', {})
                external_ids_df = pd.concat([external_ids_df, pd.DataFrame([{
                    "paperId": paper_id,
                    "DBLP": external_ids.get('DBLP'),
                    "ArXiv": external_ids.get('ArXiv'),
                    "DOI": external_ids.get('DOI'),
                    "CorpusId": external_ids.get('CorpusId'),
                    "MAG": external_ids.get('MAG'),
                    "PubMed": external_ids.get('PubMed'),
                    "PubMedCentral": external_ids.get('PubMedCentral'),
                    "ACL": external_ids.get('ACL')
                }])], ignore_index=True)

                # Process authors
                authors = paper.get('authors', [])
                if isinstance(authors, list):
                    for author in authors:
                        if isinstance(author, dict):
                            author_id = author.get('authorId')
                            author_name = author.get('name')

                            # Append to authors_df
                            if author_id is not None:
                                authors_df = pd.concat([authors_df, pd.DataFrame([{
                                    "authorId": author_id,
                                    "name": author_name
                                }])], ignore_index=True)

                                # Append to paper_authors_df
                                paper_authors_df = pd.concat([paper_authors_df, pd.DataFrame([{
                                    "paperId": paper_id,
                                    "authorId": author_id
                                }])], ignore_index=True)

# Remove duplicates in DataFrames
papers_df = papers_df.drop_duplicates()
authors_df = authors_df.drop_duplicates()
paper_authors_df = paper_authors_df.drop_duplicates()
external_ids_df = external_ids_df.drop_duplicates()

# Save DataFrames to CSV files
papers_df.to_csv(os.path.join(output_dir, "Papers.csv"), index=False)
authors_df.to_csv(os.path.join(output_dir, "Authors.csv"), index=False)
paper_authors_df.to_csv(os.path.join(output_dir, "PaperAuthors.csv"), index=False)
external_ids_df.to_csv(os.path.join(output_dir, "ExternalIds.csv"), index=False)



papers_with_ids = papers_df.merge(external_ids_df, on="paperId", how="left")

# Join PaperAuthors to Authors (INNER JOIN)
paper_author_details = paper_authors_df.merge(authors_df, on="authorId", how="inner")

# Join everything to get the full data
full_data = papers_with_ids.merge(paper_author_details, on="paperId", how="left")

# View the full data
print(full_data.head())

# Save the joined data to a CSV file
full_data.to_csv(os.path.join(output_dir, "FullData.csv"), index=False)


# Group authors by paperId and aggregate their names
authors_grouped = (
    paper_authors_df.merge(authors_df, on="authorId", how="inner")
    .groupby("paperId")["name"]
    .apply(", ".join)
    .reset_index()
    .rename(columns={"name": "authors"})
)

# Merge the grouped authors back with the papers data
papers_with_authors = papers_with_ids.merge(authors_grouped, on="paperId", how="left")

# Save the final data to CSV
final_data_with_authors = papers_with_authors.merge(paper_author_details, on="paperId", how="left").drop_duplicates()
final_data_with_authors.to_csv(os.path.join(output_dir, "PapersWithAuthors.csv"), index=False)

# View the final data
print(final_data_with_authors.head())


pdf = pd.read_csv("dblpval.csv")
pdf = pdf[pdf['data_source']=="Semantic Scholar"]
pdf['paperid'] = "null"
for idx, row in pdf.iterrows():
    pdf.at[idx,'paperid'] = row['link'].split('/')[-1]


df = pd.read_csv("dblpval.csv")
df = pdf[pdf['data_source']=="Semantic Scholar"]
df['paperid'] = "null"
for idx, row in pdf.iterrows():
    df.at[idx,'paperid'] = row['link'].split('/')[-1]

result = df.merge(pdf[['paperid', 'publication_date']], on='paperid')
result = result.dropna(subset = 'title').drop_duplicates(subset = 'link')

result = result.drop_duplicates(subset="title")  # Correctly handles duplicates
result = result.drop("publication_date_y", axis=1)  # Drops the column by specifying axis=1
result = result.rename(columns={"publication_date_x": "publication_date"})  # Renames the column

result.to_csv("result.csv")