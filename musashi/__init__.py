import collections
import web
import os
from musashi import analytics
from musashi import api_handler

APP_ROOT = os.path.dirname(__file__)

render = web.template.render(
        os.path.join(APP_ROOT, 'templates'))

db = web.database(dbn='postgres', user='tester',
        pw='testing', db='musashi-dev')

urls = (
    '/', 'index',
    '/analyze', 'analyze',
    '/api/(.*)', 'api',
    '/(favicon.ico)', 'static',
    '/s/(.*)', 'static'
)


class index(object):

    def GET(self):
        tracks = db.select('tracks', order='sequence')
        tracks_dict = collections.defaultdict(list)
        for track in tracks:
            tracks_dict[track.sequence].append(track)
        return render.index(tracks_dict)

analyze = analytics.Analyzer
analyze.db = db
analyze.render = render

api = api_handler.Api
api.db = db

class static(object):
    content_types = {
        '.js': 'text/javascript',
        '.css': 'text/css',
        '.ico': 'image/x-icon'
    }

    def GET(self, path):
        to_serve = os.path.join(APP_ROOT, 'static',
            os.path.normpath(path))
        _, ext = os.path.splitext(to_serve)
        try:
            web.header('Content-type', self.content_types[ext])
        except KeyError:
            web.header('Content-type', 'text/plain')
        return open(to_serve).read()

app = web.application(urls, globals())
run = app.wsgifunc()

if __name__ == '__main__':
    app.run()

