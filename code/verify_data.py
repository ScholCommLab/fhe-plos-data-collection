# coding: utf-8

# Some sanitiy checks to validate collected data

import pandas as pd

input_csv = "../data/plos2016.csv"
urls_csv = "../data/urls.csv"
query_csv = "../data/queries.csv"
og_csv = "../data/og_objects.csv"
altmetric_csv = "../data/altmetric.csv"

articles = pd.read_csv(input_csv, index_col="doi",
                       parse_dates=['publication_date'])
urls = pd.read_csv(urls_csv, index_col="url_id", parse_dates=['added_on'])
queries = pd.read_csv(query_csv, index_col="query_id",
                      parse_dates=['queried_at'])
og_objects = pd.read_csv(og_csv, index_col="og_id", parse_dates=[
                         'og_updated_time', 'received_at'])

am = pd.read_csv(altmetric_csv, index_col="doi")

# Articles

years = articles.publication_date.map(lambda x: x.year)


def verify(message, val):
    print("- {}: {}".format(message, val))


print("=== Checking articles ===")
verify("All articles from 2016", (years == 2016).all())
verify("All DOIs unique", articles.index.duplicated().sum() == 0)

print("\n=== Checking urls ===")
verify("8 URLs per article", (urls.groupby("doi")['type'].count() == 8).all())
verify("Unique URL ids", urls.index.duplicated().sum() == 0)
verify("Unique URLs", urls.url.duplicated().sum() == 0)

print("\n=== Checking queries ===")
verify("Unique query ids", queries.index.duplicated().sum() == 0)

print("\n=== Checking og_objects ===")
verify("Unique query ids", og_objects.query_id.duplicated().sum() == 0)
