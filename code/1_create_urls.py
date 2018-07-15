import csv
import datetime
import pandas as pd
from tqdm import tqdm


input_csv = "../data/plos.csv"
urls_csv = "../data/urls.csv"

templates = {"doi": "https://doi.org/{}",
             "doi_old": "http://dx.doi.org/{}",
             "landing": "http://journals.plos.org/plosone/article?id={}",
             "authors": "http://journals.plos.org/plosone/article/authors?id={}",
             "metrics": "http://journals.plos.org/plosone/article/metrics?id={}",
             "comments": "http://journals.plos.org/plosone/article/comments?id={}",
             "related": "http://journals.plos.org/plosone/article/related?id={}",
             "pdf": "http://journals.plos.org/plosone/article/file?id={}&type=printable"}

plos2016 = pd.read_csv(input_csv)
plos2016 = plos2016.set_index("doi")
plos2016['publication_date'] = plos2016['publication_date'].map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ"))
plos2016['created_on'] = datetime.datetime.now()

with open(urls_csv, "w") as urls_file:
    writer = csv.writer(urls_file, delimiter=",")
    writer.writerow(["url_id", "doi", "url", "type", "added_on"])

    i = 0
    for doi in tqdm(plos2016.index.tolist()):
        for type, template in templates.items():
            writer.writerow([i, doi, template.format(doi), type, datetime.datetime.now()])
            i = i + 1
