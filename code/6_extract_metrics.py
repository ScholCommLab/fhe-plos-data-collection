import json
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

tqdm.pandas()


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


# Directories and Files
base_dir = Path("../data/pipeline/")
altmetric_csv = base_dir / "altmetric_responses.csv"

process_dir = Path("../data/processed/")
details_csv = process_dir / "details.csv"
am_metrics_csv = process_dir / "am_metrics.csv"
fb_metrics_csv = process_dir / "fb_metrics.csv"

# Read required files
print("Reading files from disk")
details = pd.read_csv(details_csv, index_col="id")
am_raw = pd.read_csv(altmetric_csv, index_col="doi")

# Extract metrics from altmetrics responses
am_metrics = am_raw.progress_apply(extract_metrics, axis=1)

# Drop unneeded columns
del am_metrics['am_resp']
del am_metrics['am_err']
del am_metrics['ts']

am_metrics.to_csv(am_metrics_csv)

# Extract FB metrics
cols = ['shares', 'reactions', 'comments', 'plugin_comments']

# replace all zeros with NaNs, drop rows with only NaNs.
metrics = details.reset_index().dropna(how="all", subset=cols)

# drop each row that has a duplicate DOI and OG ID pair
metrics = metrics.drop_duplicates(subset=['doi', 'og_id', 'shares', 'reactions', 'comments'])

# sum up engagement counts for each DOI
metrics = metrics.groupby("doi")[cols].sum()

metrics.to_csv(fb_metrics_csv)
