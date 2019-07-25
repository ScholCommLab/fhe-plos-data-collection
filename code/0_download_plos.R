require(rplos)

start_year = 2015
end_year = 2017
output_dir = "../data/pipeline/plos_raw/"

for (year in seq(start_year, end_year, 1)) {
    print(paste("Collecting", year))
    pub_dates = paste0('publication_date:[', year, '-01-01T00:00:00Z TO ', year, '-12-31T23:59:59Z]')
    journal = 'journal_key:PLoSONE'
    doc_type = 'doc_type:full'

    fl = 'id,publication_date,title,author,subject,subject_level_1'
    fq = list(journal, pub_dates, doc_type)

    numFound = searchplos(q="*:*", fl=fl, fq=fq, limit=0)$meta$numFound
    print(paste("Found", numFound, "articles"))

    doi = c()
    publication_date = c()
    author = c()
    title = c()

    r = searchplos(q="*:*", fl=fl, fq=fq, limit=numFound, progress=httr::progress())
    write.csv(unique(r$data), paste0(output_dir, "plos", year, ".csv"), row.names = FALSE)
}