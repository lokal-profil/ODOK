#!/usr/bin/python
# -*- coding: utf-8  -*-
'''
Identifies and lists contributors to list articles
TODO:
    Merge into synking
'''

import codecs
import json
import common
import WikiApi as wikiApi
import dconfig as config


def run(start='2015-01-01', end=None):
    # connect to api
    wpApi = wikiApi.WikiApi.setUpApi(user=config.w_username,
                                     password=config.w_password,
                                     site=config.wp_site)

    # find changed pages
    pageList = wpApi.getEmbeddedin(u'Mall:Offentligkonstlista', 0)

    contribs, ministats = handleContributions(wpApi,
                                              pageList,
                                              start='2015-01-01')

    f = codecs.open('contribs.json', 'w', 'utf8')
    f.write(json.dumps(contribs))
    print json.dumps(ministats, indent=4)


def handleContributions(wpApi, pageList, start=None, end=None):
    '''
    Given a pagelist get all off the contribution statistics
    '''
    # validate input
    if start is not None:
        if not common.is_iso_date(start):
            print 'start was not a valid YYYY-MM-DD date'
            exit
        start = str(start)  # in case of unicode
    if end is not None:
        if not common.is_iso_date(end):
            print 'end was not a valid YYYY-MM-DD date'
            exit
        end = str(end)  # in case of unicode

    # get all stats
    dDict = {}
    for p in pageList:
        dDict[p] = wpApi.getContributions(p, start=start, end=end)

    # ministats
    ministats = {}
    ministats['pages'] = len(dDict.keys())
    anons_all = []
    users_all = []
    ministats['users_contribs'] = 0
    ministats['size_abs'] = 0
    ministats['size_rel'] = 0
    for page, stats in dDict.iteritems():
        if stats is None:
            continue
        anons_all += stats['users']['_anon']
        del stats['users']['_anon']
        users_all += stats['users'].keys()
        ministats['users_contribs'] += sum(stats['users'].values())
        ministats['size_abs'] += stats['size']['absolute']
        ministats['size_rel'] += stats['size']['relative']
    anons_all = list(set(anons_all))
    users_all = list(set(users_all))
    ministats['users'] = len(users_all)
    ministats['anons'] = len(anons_all)

    return dDict, ministats

if __name__ == "__main__":
    import sys
    usage = '''Usage: python contributors.py start end
\tstart (optional): YYYY-MM-DD start date (default 2015-01-01)
\tend (optional): YYYY-MM-DD end date (default None)'''
    argv = sys.argv[1:]
    if len(argv) == 0:
        run()
    elif len(argv) == 1:
        run(start=argv[0])
    elif len(argv) == 2:
        run(start=argv[0], end=argv[1])
    else:
        print usage
# EoF