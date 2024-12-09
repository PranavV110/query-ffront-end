from scrapers.semantic_scholar_scraper.semantic_scholar_scraper import SemanticScholarScraper
from scrapers.core import AuthorInfo
import pandas as pd
import datetime as dt
import pickle
import os
from pathlib import Path

# Input CSV file
faculty_file = "combined_data.csv"

# Load data from CSV
data = pd.read_csv(faculty_file, delimiter=",", encoding="utf-8")

# Prepare author list
author_list = [(row["Name"], row["Url"]) for _, row in data.iterrows()]

# Set base and new target folder for pickled data
script_path = Path(__file__).resolve()
base_dir = script_path.parent.parent
new_target_folder_path = os.path.join(base_dir, "new_pkl_files")
os.makedirs(new_target_folder_path, exist_ok=True)

# Define date range for scraping
start_date = dt.datetime(2024, 8, 13)
end_date = dt.datetime(2024, 12, 4)

# Run Semantic Scholar scraper and save only new files
SemanticScholarScraper.get_papers(author_list, start_date, end_date, new_target_folder_path)

# Load only new papers
all_papers = []
for filename in os.listdir(new_target_folder_path):
    if filename.endswith('.pkl'):
        filepath = os.path.join(new_target_folder_path, filename)
        with open(filepath, 'rb') as file:
            papers = pickle.load(file)
            all_papers.extend(papers)

# Group papers by authors
papers_by_authors = {}
for item in all_papers:
    if item.full_name not in papers_by_authors:
        papers_by_authors[item.full_name] = []
    papers_by_authors[item.full_name].append(item)

# Save papers to CSV
df = pd.DataFrame([vars(item) for item in all_papers])
output_file = os.path.join(base_dir, "new_sem_sch_collection.csv")
df.to_csv(output_file, index=False, encoding="utf-8")
