#!/usr/bin/env python2.7

import os.path
from musashi import api_handler

if __name__ == '__main__':
    methods = api_handler.Api().methods
    docs = dict()
    for base in methods:
        for meth in methods[base]:
            docs['/'.join([base, meth])] = methods[base][meth].func_doc
    with open(os.path.expanduser('~/Dropbox/Public/api.txt'), 'w') as f:
        for url in docs:
            f.write("URL /{0}:\n".format(url))
            f.write(docs[url])
            f.write("\n")
