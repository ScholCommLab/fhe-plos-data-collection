
# coding: utf-8


import configparser
import csv
import datetime
import json
from pathlib import Path

import pandas as pd

from Altmetric import Altmetric

from tqdm.auto import tqdm
tqdm.pandas()


Config = configparser.ConfigParser()
Config.read('../config.cnf')
ALTMETRIC_KEY = Config.get('altmetric', 'key')

altmetric = Altmetric(api_key=ALTMETRIC_KEY)

base_dir = Path("../data/pipeline/")
infile = base_dir / "articles.csv"
outfile = base_dir / "altmetric_responses.csv"


articles = pd.read_csv(infile, index_col="doi")


with open(str(outfile), "w") as f:
    csv_writer = csv.writer(f, delimiter=",")
    csv_writer.writerow(['doi', 'am_resp', 'am_err', 'ts'])

    for doi in tqdm(articles.index.tolist()):
        try:
            am_resp = altmetric.doi(doi=doi, fetch=True)
            am_err = None
        except Exception as e:
            am_resp = None
            am_err = e
        now = datetime.datetime.now()
        csv_writer.writerow(
            [doi, json.dumps(am_resp), str(am_err), str(now)])
