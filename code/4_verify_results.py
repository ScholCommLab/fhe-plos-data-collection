# coding: utf-8

# Some sanitiy checks to validate collected data

import pandas as pd
from pathlib import Path

base_dir = Path("../data/")

input_csv = base_dir / "plos_ncbi.csv"
urls_csv = base_dir / "urls.csv"
query_csv = base_dir / "queries.csv"
og_csv = base_dir / "og_objects.csv"
altmetric_csv = base_dir / "altmetric.csv"

articles = pd.read_csv(str(input_csv), index_col="doi", parse_dates=['publication_date'])
urls = pd.read_csv(str(urls_csv), index_col="url_id", parse_dates=['added_on'])
queries = pd.read_csv(str(query_csv), index_col="query_id", parse_dates=['queried_at'])
og_objects = pd.read_csv(str(og_csv), parse_dates=['og_updated_time', 'received_at'])
am = pd.read_csv(str(altmetric_csv), index_col="doi")


def verify(message, val):
    print("- {}: {}".format(message, val))


print("=== Checking articles ===")
verify("All DOIs unique", articles.index.duplicated().sum() == 0)

print("\n=== Checking urls ===")
verify("8 URLs per article", (urls.groupby("doi")['type'].count() == 8).all())
verify("Unique URL ids", urls.index.duplicated().sum() == 0)
verify("Unique URLs", urls.url.duplicated().sum() == 0)

print("\n=== Checking queries ===")
verify("Unique query ids", queries.index.duplicated().sum() == 0)

print("\n=== Checking og_objects ===")
verify("Unique query ids", og_objects.query_id.duplicated().sum() == 0)
