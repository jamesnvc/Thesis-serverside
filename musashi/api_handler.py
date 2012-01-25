import json
import web
from musashi import analytics


class Api(object):

    db = None
    analyzer = analytics.Analyzer()

    def get_catalog(self, args):
        # TODO: Filter which the requester can see?
        tracks = self.db.select('tracks')
        return self.to_json(tracks)

    def get_preview(self, args):
        pass

    def get_full(self, args):
        pass

    def analyze_workout(self, args):
        track_ids = json.loads(args.tracks)
        tracks, analysis, fatigue = self.analyzer.perform_analysis(track_ids)
        return json.dumps({'analysis': analysis, 'fatigue': list(fatigue)})

    def recommend_tracks(self, args):
        pass

    def export_workout(self, args):
        pass

    def recieve_ratings(self, args):
        pass

    def recieve_history(self, args):
        pass

    methods = {
        'get': {
            'catalog': get_catalog,
            'preview': get_preview,
            'full': get_full
        },
        'analyze': {
            'analyze': analyze_workout,
            'recommend': recommend_tracks
        },
        'export': {
            'zip': export_workout
        },
        'upload': {
            'ratings': recieve_ratings,
            'history': recieve_history
        }
    }

    def to_json(self, results):
        """Convert an iterator of StorageObjects to JSON"""
        return json.dumps([dict(res.items()) for res in results])

    def handler(self, path):
        action, subaction = path.split('/')
        web.header('Content-type', 'application/json')
        args = web.input()
        print "Calling {0}/{1} with args {2}".format(action, subaction, args)
        return self.methods[action][subaction](self, args)

    def POST(self, path):
        return self.handler(path)

    def GET(self, path):
        return self.handler(path)
