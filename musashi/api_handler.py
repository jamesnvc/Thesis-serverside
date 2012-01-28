import json
import web
from musashi import analytics


# TODO: User accounts?
class Api(object):

    db = None
    analyzer = analytics.Analyzer()

    def get_catalog(self, _):
        """Handle a request to get a list of the available tracks.

        Returns:
            A JSON list of tracks available.
        """
        # TODO: Filter which the requester can see?
        tracks = self.db.select('tracks')
        return self.to_json(tracks)

    def get_preview(self, args):
        """Handle a request to get previews of a given track or tracks.

        Arguments:
            - args: web input with a `tracks` field which is a JSON list of
              track ids.

        Returns:
            A json list of track preview data.
        """
        pass

    def get_full(self, args):
        """Handle a request to get full versions of a given track or tracks.

        Arguments:
            - args: web input with a `tracks` field which is a JSON list of
              track ids.

        Returns:
            A json list of full track data.
        """
        pass

    def analyze_workout(self, args):
        """Analyze a given workout.

        - args: web input with a `tracks` field which is a JSON list of track
                ids.
        """
        track_ids = json.loads(args.tracks)
        tracks, analysis, fatigue = self.analyzer.perform_analysis(track_ids)
        return json.dumps({'analysis': analysis, 'fatigue': list(fatigue)})

    def recommend_tracks(self, args):
        """Given a partial list of tracks, give a recommendation for the rest
        of the workout.

        Arguments:
            - args: web input with a `tracks` field which is a JSON list of
              track ids.

        Returns:
            A json list of track ids for the recommended workout.
        """
        pass

    def export_workout(self, args):
        """Request that the workout be exported into a pdf and movie.

        Arguments:
            - args: web input with a `tracks` field which is a JSON list of track ids.

        Returns:
            A URL where a zip file of the exported workout can be downloaded.
        """
        pass

    def recieve_ratings(self, args):
        """Upload a list of ratings the user has for the given tracks.

        Arguments:
            - args: web input with a `track_ratings` field which is a JSON list
              of [track id, rating] pairs.
        """
        pass

    def recieve_history(self, args):
        """Upload a workout & associate with the current user's history.

        Arguments:
            - args: web input with a `tracks` field which is a JSON list of
              track ids.
        """
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
