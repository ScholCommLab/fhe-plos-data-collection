import pandas as pd
from pathlib import Path

base_dir = Path("../data/")
input_dir = base_dir / "plos_raw/"

print("Loading RAW PLoS datasets for each year")

dfs = []
for i in range(2013, 2018):
    df = pd.read_csv(input_dir / "plos{}.csv".format(i), index_col="id")
    df.index.name = "doi"
    dfs.append(df)
df = pd.concat(dfs)

print("Loading NCBI DOI-Lookup dataset")
ncbi_ids = pd.read_csv(base_dir / "PMC-ids.csv")[['DOI', 'PMCID', 'PMID']]

ncbi_ids = ncbi_ids[ncbi_ids.DOI.isin(df.index)]
ncbi_ids.columns = ["doi", "pmcid", "pmid"]
ncbi_ids = ncbi_ids.set_index("doi")

print("Merging and writing plos.csv")
f = df.merge(ncbi_ids, left_index=True, right_index=True, how="left")
f.to_csv(base_dir / "plos_ncbi.csv")