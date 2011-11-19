import web
import os

APP_ROOT = os.path.dirname(__file__)

render = web.template.render(
        os.path.join(APP_ROOT, 'templates'))

db = web.database(dbn='postgres', user='tester',
        pw='testing', db='musashi-dev')

urls = (
    '/', 'index',
    '/s/(.*)', 'static'
)


class index(object):
    def GET(self):
        tracks = [map(chr, range(ord('a'), ord('d'))) for i in xrange(0, 12)]
        return render.index(tracks)


class static(object):
    content_types = {
        '.js': 'text/javascript',
        '.css': 'text/css'
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

if __name__ == '__main__':
    app.run()
