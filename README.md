# Facebook Hidden Engagement - PLOS ONE

Scripts to collect and analyse data used to investigate the difference between public and private engagement numbers for PLOS ONE publications in the year 2016.

## Some notes

- Collected all PLoS ONE articles for the specified years using the r-package [rplos](https://github.com/ropensci/rplos).

- NCBI's [FTP Service](https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/) provides the file [PMC-ids.csv.gz](ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz) which we use to look up PMC IDs and PubMed IDs.

- Altmetric.com key needed to collect public engagement.

- Facebook User generated token needed to collect private engagement. Head over to the [Graph API Explorer](https://developers.facebook.com/tools/explorer/) to generate one with your account.