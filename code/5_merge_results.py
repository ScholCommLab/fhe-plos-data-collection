# coding: utf-8

# Some sanitiy checks to validate collected data

import json
from pathlib import Path

import pandas as pd
from tqdm.auto import tqdm

tqdm.pandas()

# Directories and Files
base_dir = Path("../data/pipeline/")
process_dir = Path("../data/processed/")

input_csv = base_dir / "articles.csv"
urls_csv = base_dir / "urls.csv"
query_csv = base_dir / "queries.csv"
og_csv = base_dir / "fb_objects.csv"
altmetric_csv = base_dir / "altmetric_responses.csv"

details_csv = process_dir / "details.csv"

# Load files
articles = pd.read_csv(input_csv, index_col="doi", parse_dates=['publication_date'])
urls = pd.read_csv(urls_csv, index_col="url_id", parse_dates=['added_on'])
queries = pd.read_csv(query_csv, index_col="query_id", parse_dates=['queried_at'])
og_objects = pd.read_csv(og_csv, index_col="og_id", parse_dates=['og_updated_time', 'received_at'])

# Convert to numerical columns
num_cols = ['reactions', 'shares', 'comments', 'plugin_comments']
og_objects[num_cols] = og_objects[num_cols].astype(int)

# Merge data frames
a = og_objects.merge(queries, left_on="query_id", right_index=True, how="left")
b = a.merge(urls, left_on="url_id", right_index=True, how="left")
c = b.merge(articles, left_on="doi", right_index=True, how="left")
c.index.name = "id"

# Write output
c.to_csv(details_csv)
