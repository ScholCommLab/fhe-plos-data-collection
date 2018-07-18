
# coding: utf-8


import configparser
import csv
import datetime
import json
from pathlib import Path

import pandas as pd

from Altmetric import Altmetric

try:
    # for notebook
    get_ipython
    from tqdm._tqdm_notebook import tqdm_notebook as tqdm
except:
    # for commandline
    from tqdm import tqdm
tqdm.pandas()


Config = configparser.ConfigParser()
Config.read('../config.cnf')
ALTMETRIC_KEY = Config.get('altmetric', 'key')

altmetric = Altmetric(api_key=ALTMETRIC_KEY)

base_dir = Path("../data/")
infile = base_dir / "plos_ncbi.csv"
outfile = base_dir / "altmetric.csv"


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
