import collections
import web


class Analyzer(object):

    db = None
    render = None

    def exercise_targets(self, exercise):
        """Get the targets corresponding to the given exercise."""
        move_ids = [move.id for move in exercise.moves]
        targets = self.db.select(
                ['targets', 'move_target'],
                where=("targets.id = move_target.target_id AND "
                       "move_target.move_id IN $move_ids"),
                vars=dict(move_ids=move_ids))
        return [(target.name, exercise.gear) for target in targets]

    def fatigue_analysis(self, tracks):
        targets = self.db.select('targets')
        health = dict()
        for target in targets:
            health[target.name] = 10
        health_seq = list()
        for track in tracks.values():
            for exercise in track.values():
                for target in health:
                    if health[target] < 10:
                        health[target] += 1
                for target, gear in exercise:
                    health[target] -= gear
                health_seq.append(health.copy())
        return reversed(health_seq)


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

    def perform_analysis(self, track_ids):
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
                for exercise in block.exercises:
                    exercise.moves = list(self.db.select(
                        'moves', where="exercise_id = $exercise_id",
                        order='sequence', vars=dict(exercise_id=exercise.id)))
        analysis, fatigue = self.analyze(tracks)
        return (tracks, analysis, fatigue)

    def POST(self):
        """Service the request."""
        track_ids = map(int, web.input().tracks.split('-'))
        tracks, analysis, fatigue =  self.perform_analysis(track_ids)
        track_info = self.render.workout_tracks(tracks, analysis, fatigue, self.render)
        web.header('Content-type', 'text/html')
        return track_info
