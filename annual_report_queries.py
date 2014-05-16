#!/usr/bin/env python

# Author: Dan Leehr (dan.leehr@nescent.org)
# 2014-05-16
#
# For a given year, executes the PostgreSQL queries to calculate statistics
# as described on http://wiki.datadryad.org/Annual_Statistics_Reports
#
# Uses psql command-line tool instead of a python library like psycopg2.
# Not suitable for connecting to a web application - this script executes system commands
# and does NOT protect against injection attacks.

import os, sys

def dict_from_query(sql):
    cmd = "psql -A -U dryad_app dryad_repo -c \"%s\"" % sql
    output = [line.strip().split('|') for line in os.popen(cmd).readlines()]
    if len(output) == 1:
        return None
    else:
        return dict(zip(output[0],output[1]))

def get_dc_schema_id():
    sql = "select metadata_schema_id from metadataschemaregistry where short_id = 'dc'"
    d = dict_from_query(sql)
    return d['metadata_schema_id']

def get_datapackage_collection_id():
    sql = "select collection_id from collection where name = 'Dryad Data Packages'"
    d = dict_from_query(sql)
    return d['collection_id']

def get_metadata_field_id(schema_id, element, qualifier=None):
    if qualifier is None:
        qualifier_clause = "qualifier is null"
    else:
        qualifier_clause = "qualifier = '%s'" % qualifier

    sql = "select metadata_field_id from metadatafieldregistry where metadata_schema_id = '%s' " \
          "and element = '%s' and %s" % (schema_id, element, qualifier_clause)
    d = dict_from_query(sql)
    return d['metadata_field_id']

def get_author_count(year):
    collection_id = get_datapackage_collection_id()
    begin_date = "%d-01-00" % year
    end_date = "%d-01-00" % (year + 1)
    dc_schema_id = get_dc_schema_id()
    author_metadata_field_id = get_metadata_field_id(dc_schema_id,'contributor','author')
    date_accessioned_metadata_field_id = get_metadata_field_id(dc_schema_id,'date','accessioned')
    sql = "select count(distinct text_value) as author_count from metadatavalue where metadata_field_id=%s " \
          "and item_id in " \
          "(select item_id from collection2item where collection_id=%s and item_id in " \
          "(select item_id from metadatavalue where metadata_field_id = %s " \
          "and text_value > '%s' " \
          "and text_value < '%s'))" % \
          (author_metadata_field_id, collection_id, date_accessioned_metadata_field_id, begin_date, end_date)
    d = dict_from_query(sql)
    return d['author_count']


def get_total_authors_represented():
    '''
    This doesn't check anything against calendar years
    '''
    collection_id = get_datapackage_collection_id()
    dc_schema_id = get_dc_schema_id()
    author_metadata_field_id = get_metadata_field_id(dc_schema_id,'contributor','author')
    sql = "select count(distinct text_value) as author_count from metadatavalue where metadata_field_id=%s " \
          "and item_id in " \
          "(select item_id from collection2item where collection_id=%s)" % \
          (author_metadata_field_id, collection_id)
    d = dict_from_query(sql)
    return d['author_count']

def accounts_with_id_below(eperson_id):
    sql = "select count(*) as person_count from eperson where eperson_id < %s" % eperson_id
    d = dict_from_query(sql)
    return d['person_count']

def get_accounts_created(year):
    # Last account in 2013 by email was qiuqiang@lzu.edu.cn, eperson_id 6701
    # First account of 2014 by email was katrinewhiteson@gmail.com, eperson_id 6717
    # Either I'm missing a lot of the emails or the ids are not sequential
    # Thought we could count the number active up to the end of 2013 and subtract the
    # total that was reported for 2012.
    # May be able to get it out of apache logs.
    return 'Unknown'

def get_total_accounts():
    sql = "select count(*) as person_count from eperson"
    d = dict_from_query(sql)
    return d['person_count']

def get_top_author_distribution():
    try:
        import dryad_solr_client
        return dryad_solr_client.distribution_of_packages_by_author()
    except BaseException:
        return None

def print_top_authors():
    distribution = get_top_author_distribution()
    if distribution is None:
        print "Unable to run solr client to get top author distribution."
        print "Make sure dependencies (requests) are installed, or run elsewhere."
    else:
        print ''
        for d in distribution:
            print '%s - %s' % (d['packages'], d['author'])

def main(year):
    print "Authors associated with submissions in %d: %s" % (year, get_author_count(year))
    print "Total authors represented in Dryad: %s" % get_total_authors_represented()
    print "Total accounts: %s" % get_total_accounts()
    print "Accounts created in %d: %s" % (year, get_accounts_created(year))
    print "Top authors by package count: "
    print_top_authors()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s <year>" % sys.argv[0]
    else:
        main(int(sys.argv[1]))

