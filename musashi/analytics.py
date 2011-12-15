import collections
import web


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
        return [(target.name, exercise.gear) for target in targets]

    def fatigue_analysis(self, tracks):
        targets = self.db.select('targets')
        health = dict()
        for target in targets:
            health[target.name] = 10
        health_seq = list()
        for track in tracks:
            for exercise in track:
                for target, gear in exercise:
                    health[target] -= gear
                health_seq.append(health.copy())
        return health_seq


    def analyze(self, tracks):
        """Run the analysis on the selected tracks."""
        analysis = collections.defaultdict(list)
        for track in tracks:
            analysis[track.id] = collections.defaultdict(list)
            for block in track.blocks:
                for exercise in block.exercises:
                    analysis[track.id][exercise.id] = self.exercise_targets(
                            exercise)
        fatigue = self.fatigue_analysis(analysis)
        return (analysis, fatigue)

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
        analysis, _ = self.analyze(tracks)
        track_info = self.render.workout_tracks(tracks, analysis, self.render)
        web.header('Content-type', 'text/html')
        return track_info
