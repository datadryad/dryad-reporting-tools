#!/usr/bin/env python
__author__ = 'dan'

import requests
from xml.etree import ElementTree

SOLR_URL = 'http://datadryad.org:8080/solr/search/'

def extract_name(author_field):
    '''
    'bernatchez, louis|||Bernatchez, Louis' -> Bernatchez, Louis
    '''
    return author_field.split('|')[-1]

def distribution_of_packages_by_author():
    '''
    Perform an empty search, and look at the author facet.
    Empty search, extracted via debugging AbstractSearch.java:571
    '''
    solr_query = SOLR_URL + "select/?q=DSpaceStatus%3AArchived&facet.limit=20&facet.mincount=1&facet=true" \
                            "&facet.field=dc.contributor.author_filter&facet.field=dc.subject_filter" \
                            "&facet.field=prism.publicationName_filter&facet.field=%7B%21ex%3Ddt%7Dlocation.coll" \
                            "&facet.query=dc.date.issued.year%3A%5B2000+TO+2014%5D" \
                            "&facet.query=dc.date.issued.year%3A%5B1904+TO+1999%5D&fq=-location%3Al3" \
                            "&fq=archived%3Atrue&fq=%7B%21tag%3Ddt%7Dlocation.coll%3A2" \
                            "&rows=20&sort=score+asc&start=0&f.location.coll.facet.mincount=0"
    # Execute the search
    response = requests.get(solr_query)
    root = ElementTree.fromstring(response.text.encode('utf-8'))
    contributing_authors = root.findall("./lst[@name='facet_counts']/lst[@name='facet_fields']/lst[@name='dc.contributor.author_filter']")[0]
    distribution = []
    for author in contributing_authors:
        distribution.append({
            'author': extract_name(author.attrib['name']),
            'packages': int(author.text)
        })
    return distribution

if __name__ == '__main__':
    for d in distribution_of_packages_by_author():
        print "Author: %s\t, Packages: %s" % ( d['author'], d['packages'])
