# coding: utf-8

# Some sanitiy checks to validate collected data

from pathlib import Path
import pandas as pd
import json
from tqdm.auto import tqdm
tqdm.pandas()

base_dir = Path("../data/pipeline/")
process_dir = Path("../data/processed/")

input_csv = base_dir / "plos_ncbi.csv"
urls_csv = base_dir / "urls.csv"
query_csv = base_dir / "queries.csv"
og_csv = base_dir / "og_objects.csv"
altmetric_csv = base_dir / "altmetric.csv"

metrics_csv = process_dir / "metrics.csv"
details_csv = process_dir / "details.csv"

articles = pd.read_csv(input_csv, index_col="doi", parse_dates=['publication_date'])
urls = pd.read_csv(urls_csv, index_col="url_id", parse_dates=['added_on'])
queries = pd.read_csv(query_csv, index_col="query_id", parse_dates=['queried_at'])
og_objects = pd.read_csv(og_csv, index_col="og_id", parse_dates=['og_updated_time', 'received_at'])

articles = pd.read_csv(input_csv, index_col="doi", parse_dates=['publication_date'])
urls = pd.read_csv(urls_csv, index_col="url_id", parse_dates=['added_on'])
queries = pd.read_csv(query_csv, index_col="query_id", parse_dates=['queried_at'])
og_objects = pd.read_csv(og_csv, parse_dates=['og_updated_time', 'received_at'])

num_cols = ['reactions', 'shares', 'comments', 'plugin_comments']
og_objects[num_cols] = og_objects[num_cols].astype(int)

a = og_objects.merge(queries, left_on="query_id", right_index=True, how="left")
b = a.merge(urls, left_on="url_id", right_index=True, how="left")
c = b.merge(articles, left_on="doi", right_index=True, how="left")
c.index.name = "id"

c.to_csv(details_csv)


def extract_metrics(row):
    try:
        resp = json.loads(row['am_resp'])
        medias = resp['counts'].keys()
        for media in medias:
            if 'posts_count' in resp['counts'][media]:
                row[media] = resp['counts'][media]['posts_count']
    except:
        return row

    return row


am_raw = pd.read_csv(altmetric_csv, index_col="doi")
am = am_raw.progress_apply(extract_metrics, axis=1)

del am['am_resp']
del am['am_err']
del am['ts']

metrics = am

x = ['shares', 'comments', 'reactions']
for _ in x:
    metrics[_] = c.reset_index().groupby(["doi", "og_id"]).first().groupby(["doi"]).sum()[_]

metrics['diff'] = metrics['shares'] - metrics.facebook
metrics.to_csv("../data/metrics.csv")