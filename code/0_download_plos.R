require(rplos)

year = "2016"
pub_dates = paste0('publication_date:[', year, '-01-01T00:00:00Z TO ', year, '-12-31T23:59:59Z]')
journal = 'journal_key:PLoSONE'
doc_type = 'doc_type:full'

fl = 'id,publication_date,title,author'
fq = list(journal, pub_dates, doc_type)
batch_size = 500

numFound = searchplos(q="*:*", fl=fl, fq=fq, limit=0)$meta$numFound
print(paste("Found", numFound, "articles"))

id = c()
publication_date = c()
author = c()
title = c()

for (i in seq(0, numFound, batch_size)) {
  r = searchplos(q="*:*", fl=fl, fq=fq, start=i, limit=batch_size, sleep=6)
  
  print(paste("Saved", length(r$data$id), "entries"))
  
  id = c(id, r$data$id)
  publication_date = c(publication_date, r$data$publication_date)
  author = c(author, r$data$author)
  title = c(title, r$data$title)
}

plos2016 = data.frame(doi=id, publication_date=publication_date, title=title, author=author)
write.csv(plos2016, "../data/plos.csv", row.names = FALSE)