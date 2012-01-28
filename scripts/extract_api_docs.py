#!/usr/bin/env python2.7

from musashi import api_handler

if __name__ == '__main__':
    methods = api_handler.Api().methods
    docs = dict()
    for base in methods:
        for meth in methods[base]:
            docs['/'.join([base, meth])] = methods[base][meth].func_doc
    for url in docs:
        print "URL /{0}:".format(url)
        print docs[url]
        print
