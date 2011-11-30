import web
import collections


class Analyzer(object):

    db = None
    render = None

    def exercise_targets(self, exercise):
        """Get the targets corresponding to the given exercise."""
        targets = self.db.select(
                ['targets', 'exercise_target'],
                where=("targets.id = exercise_target.target_id AND "
                       "$exercise_id = exercise_target.exercise_id"),
                vars=dict(exercise_id=exercise.id))
        return [target.name for target in targets]

    def analyze(self, tracks):
        """Run the analysis on the selected tracks."""
        track_ids = [track.id for track in tracks]
        exercises = self.db.select(
                'exercises',
                where="exercises.id IN $track_ids",
                order="start_time",
                vars=dict(track_ids=track_ids))
        analysis = collections.defaultdict(list)
        for track in tracks:
            analysis[track.id] = collections.defaultdict(list)
            for exercise in exercises:
                analysis[track.id][exercise.id] = self.exercise_targets(
                        exercise)
        return analysis

    def POST(self):
        """Service the request."""
        track_ids = map(int, web.input().tracks.split('-'))
        # Need to wrap this in a list so we can traverse it multiple times
        tracks = list(self.db.select('tracks', where="id in $ids",
                vars=dict(ids=track_ids)))
        for track in tracks:
            # Ditto
            track.blocks = list(self.db.select(
                    'blocks', where="track_id = $track_id",
                    order='sequence', vars=dict(track_id=track.id)))
            for block in track.blocks:
                block.exercises = list(self.db.select(
                    'exercises', where="block_id = $block_id",
                    order='start_time',
                    vars=dict(block_id=block.id)))
        analysis = self.analyze(tracks)
        track_info = self.render.workout_tracks(tracks, analysis, self.render)
        web.header('Content-type', 'text/html')
        return track_info
