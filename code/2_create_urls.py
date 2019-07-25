import csv
import datetime
import math
from pathlib import Path
import numpy as np

import pandas as pd
from tqdm.auto import tqdm
tqdm.pandas()

base_dir = Path("../data/pipeline/")
input_csv = base_dir / "plos_ncbi.csv"
urls_csv = base_dir / "urls.csv"

templates = {"doi": "https://doi.org/{}",
             "doi_old": "http://dx.doi.org/{}",
             "landing": "http://journals.plos.org/plosone/article?id={}",
             "authors": "http://journals.plos.org/plosone/article/authors?id={}",
             "metrics": "http://journals.plos.org/plosone/article/metrics?id={}",
             "comments": "http://journals.plos.org/plosone/article/comments?id={}",
             "related": "http://journals.plos.org/plosone/article/related?id={}",
             "pdf": "http://journals.plos.org/plosone/article/file?id={}&type=printable"}

plos = pd.read_csv(input_csv, index_col="doi")
plos['publication_date'] = plos['publication_date'].map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ"))
plos['created_on'] = datetime.datetime.now()

with open(str(urls_csv), "w") as urls_file:
    writer = csv.writer(urls_file, delimiter=",")
    writer.writerow(["url_id", "doi", "url", "type", "added_on"])

    i = 0
    for doi in tqdm(plos.index.tolist()):
        if not math.isnan(plos.loc[doi, "pmid"]):
            pmid = "https://ncbi.nlm.nih.gov/pubmed/{}".format(int(plos.loc[doi, "pmid"]))
            writer.writerow([i, doi, pmid, "pmid", datetime.datetime.now()])
            i += 1

        if plos.loc[doi, "pmcid"] is not np.nan:
            pmc = "https://ncbi.nlm.nih.gov/pmc/articles/{}/".format(plos.loc[doi, "pmcid"])
            writer.writerow([i, doi, pmc, "pmc", datetime.datetime.now()])
            i += 1

        for type, template in templates.items():
            writer.writerow([i, doi, template.format(doi), type, datetime.datetime.now()])
            i += 1
