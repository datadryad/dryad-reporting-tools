#!/usr/local/bin/python
#####
## purpose: check whether dryad data is available for publications
## In file requirements: same directory as script + text, named "DOIlist.txt" + one publication DOI per line
## if dryad data is available, writes dryad URL for the data file, else writes NA
## output: tab-separated txt file 
##
## Based on observation of URLS retrieved from Dryad:
## Data package available example:
## http://datadryad.org/discover?query="doi:10.1111/j.1558-5646.2007.00022.x"
## Positive: http://datadryad.org/resource/doi:10.5061/dryad.20 (a Dryad resource page)
## Data package NOT available example:
## http://datadryad.org/discover?query="doi:10.1111/j.1558-5646.2007.00023.x"
## Negative: http://datadryad.org/discover?query=%22doi:10.1111/j.1558-5646.2007.00023.x%22
#####
import urllib2
import datetime

def timeStamped(fname, fmt='%Y-%m-%d-%H-%M-%S_{fname}'):
    return datetime.datetime.now().strftime(fmt).format(fname=fname)

with open(timeStamped('dryad_data.txt'),'w') as outfile:
    outfile.write('Publication DOI\tDryad data URL\n')
    with open('DOIlist.txt', 'r') as infile:
        for line in infile:
            line = line.strip()	
            queryUrl = 'http://datadryad.org/discover?query="doi:' + line + '"'
            response = urllib2.urlopen(queryUrl)
            redirect = response.geturl()
            if line in redirect:
                outfile.write(line + '\tNA\n')
            else:
                outfile.write(line + '\t' + redirect + '\n')