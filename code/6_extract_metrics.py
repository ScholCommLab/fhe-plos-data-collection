import json
from pathlib import Path

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
am_metrics_csv = process_dir / "altmetrics_metrics.csv"
fb_metrics_csv = process_dir / "fb_metrics.csv"

# Read required files
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
metrics = details.reset_index().groupby(["doi", "og_id"]).first()
metrics = metrics.groupby(["doi"])['shares', 'reactions', 'comments'].sum()

metrics.to_csv(fb_metrics_csv)
