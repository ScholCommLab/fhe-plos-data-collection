# Facebook Hidden Engagement - PLOS ONE

Python and R scripts to collect data used to investigate the difference between public and private engagement numbers for PLOS ONE publications. Detailed description of the methodology can be found in this [conference article](https://openaccess.leidenuniv.nl/handle/1887/65189) presented at STI 2018.

More information about Hidden Engagement on Facebook and related projects can be found [here](https://github.com/ScholCommLab/facebook-hidden-engagement).

## Overview

1. Initial Data collection
   1. Collect all PLoS ONE articles for specified date range using the r-package [rplos](https://github.com/ropensci/rplos).
   2. Add identifiers provided by NCBI's [FTP Service](https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/) which provides the file [PMC-ids.csv.gz](ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz).
2. Create URLs for each article
   1. See table below for more details.
3. Collect Facebook engagement counts
   1. Facebook: Query Graph API with each URL
   2. Altmetric LLP: Query the Altmetric API with each DOI

For each article (DOI, pmid, pmcid) we create 10 different URLs which we then use to query the Facebook Graph API.

| URL type | Pattern  |                                                                       |
|----------|----------|-----------------------------------------------------------------------|
| 1        | doi      | https://doi.org/{doi}                                                 |
| 2        | doi_old  | http://dx.doi.org/{doi}                                               |
| 3        | landing  | http://journals.plos.org/plosone/article?id={doi}                     |
| 4        | authors  | http://journals.plos.org/plosone/article/authors?id={doi}             |
| 5        | metrics  | http://journals.plos.org/plosone/article/metrics?id={doi}             |
| 6        | comments | http://journals.plos.org/plosone/article/comments?id={doi}            |
| 7        | related  | http://journals.plos.org/plosone/article/related?id={doi}             |
| 8        | pdf      | http://journals.plos.org/plosone/article/file?id={doi}&type=printable |
| 9        | pubmed   | https://ncbi.nlm.nih.gov/pubmed/{pmid}                                |
| 10       | pmc      | https://ncbi.nlm.nih.gov/pmc/articles/{pmcid}/                        |

## Reproduce results

1. Run `pip install -r requirements.txt` to install python packages.
2. Install required r packages: `rplos`
3. Create `config.cnf` based on `default_config.cnf` and fill in your details
4. Set the date range in `code/0_download_plos.R`
5. Run scripts in `code` in order

## External packages and data sources

rplos:

> Scott Chamberlain, Carl Boettiger and Karthik Ram (2018). rplos: Interface to the Search API for 'PLoS' Journals. R
  package version 0.8.4. https://CRAN.R-project.org/package=rplos

Facebook Graph API

> https://developers.facebook.com/docs/graph-api/

NCBI's FTP service provides access to article identifiers:

> https://www.ncbi.nlm.nih.gov/pmc/tools/ftp

Altmetric LLP data through their API:

> https://api.altmetric.com/