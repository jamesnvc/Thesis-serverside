import base64
import bcrypt
import collections
import os
import urlparse
import web
from musashi import analytics
from musashi import api_handler

APP_ROOT = os.path.dirname(__file__)

render = web.template.render(
        os.path.join(APP_ROOT, 'templates'))

db = None
if 'HEROKU_SHARED_POSTGRESQL_AQUA_URL' in os.environ:
    db_url = urlparse.urlparse(os.environ['HEROKU_SHARED_POSTGRESQL_AQUA_URL'])
    db_params = {
                'dbn': db_url.scheme,
                'db': db_url.path[1:],
                'user': db_url.username,
                'pw': db_url.password,
                'host': db_url.hostname,
                'port': db_url.port
            }
    db = web.database(**db_params)
else:
    db = web.database(dbn='postgres', user='tester',
            pw='testing', db='musashi-dev')

urls = (
    '/', 'index',
    '/analyze', 'analyze',
    '/api/(.*)', 'api',
    '/(favicon.ico)', 'static',
    '/s/(.*)', 'static',
    '/authorize', 'auth'
)

# Basic, hacky auth
allowed = {
    'jamesnvc': '$2a$12$4covPIojRTqETBS/8QbORuRHAHuYDi/xHv/8QvZTgfFuE08K2cO8a'
}


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


def check_auth():
    auth = web.ctx.env.get('HTTP_AUTHORIZATION')
    if auth is None:
        return False
    auth = auth[6:]
    username, password = base64.decodestring(auth).split(':')
    if username in allowed:
        hashed_pw = allowed[username]
        return bcrypt.hashpw(password, hashed_pw) == hashed_pw
    return False


class static(object):
    content_types = {
        '.js': 'text/javascript',
        '.css': 'text/css',
        '.pdf': 'application/pdf',
        '.ico': 'image/x-icon'
    }

    def GET(self, path):
        to_serve = os.path.join(APP_ROOT, 'static',
            os.path.normpath(path))
        _, ext = os.path.splitext(to_serve)
        # Need to be logged in to get the pdfs
        if ext == '.pdf' and not check_auth():
                raise web.seeother(
                    '/authorize?redirect_to={0}'.format('/s/{0}'.format(path)))
        try:
            web.header('Content-type', self.content_types[ext])
        except KeyError:
            web.header('Content-type', 'text/plain')
        return open(to_serve).read()


class auth(object):

    def GET(self):
        authreq = False
        if auth is None:
            authreq = True
        else:
            if check_auth():
                path = web.input().redirect_to or '/'
                raise web.seeother(path)
            else:
                authreq = True
        if authreq:
            web.header('WWW-Authenticate','Basic realm="Musashi"')
            web.ctx.status = '401 Unauthorized'
            return

app = web.application(urls, globals())
run = app.wsgifunc()

if __name__ == '__main__':
    app.run()

