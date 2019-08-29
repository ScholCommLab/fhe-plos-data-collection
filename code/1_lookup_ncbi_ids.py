import pandas as pd
from pathlib import Path

base_dir = Path("../data/pipeline/")
input_dir = base_dir / "plos_raw/"
plos_ncbi = base_dir / "articles.csv"

pmc_ids = "../data/raw/PMC-ids.csv"

print("Loading RAW PLoS datasets for each year")

input_files = list(input_dir.glob('**/*.py'))

dfs = []
for f in input_files:
    df = pd.read_csv(f, index_col="id")
    df.index.name = "doi"
    dfs.append(df)
df = pd.concat(dfs)

print("Loading NCBI DOI-Lookup dataset")
ncbi_ids = pd.read_csv(pmc_ids)[['DOI', 'PMCID', 'PMID']]

ncbi_ids = ncbi_ids[ncbi_ids.DOI.isin(df.index)]
ncbi_ids.columns = ["doi", "pmcid", "pmid"]
ncbi_ids = ncbi_ids.set_index("doi")

print("Merging and writing plos.csv")
f = df.merge(ncbi_ids, left_index=True, right_index=True, how="left")
f.to_csv(plos_ncbi)
