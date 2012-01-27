#!/usr/bin/env python2.7
import os
import json
import urlparse
import psycopg2

seeds = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'seeds.json'))
init = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'db_init.sql'))
commas = ', '.join

db_params = {'database': 'musashi-dev', 'user': 'tester'}
if 'HEROKU_SHARED_POSTGRESQL_AQUA_URL' in os.environ:
    db_url = urlparse.urlparse('HEROKU_SHARED_POSTGRESQL_AQUA_URL')
    db_params = {
                'database': db_url.path[1:],
                'user': db_url.username,
                'password': db_url.password,
                'host': db_url.hostname,
                'port': db_url.port
            }
print "Seeding db with config {0}".format(db_params)

def int_seq(start=0):
    n = start
    while True:
        yield n
        n += 1


def insert_into(table, fields):
    return "INSERT INTO {0} ({1}) VALUES ({2});".format(
        table, commas(fields), commas(['%s'] * len(fields)))


def add_track(track, cur):
    fields = ["sequence", "release", "song", "kind", "length_minutes",
              "length_seconds"]
    cur.execute(
            insert_into('tracks', fields),
            [track[field] for field in fields])


def add_block(block, cur):
    cur.execute(
        "SELECT id FROM tracks WHERE sequence = %s AND release = %s;",
        (block['track']['sequence'], block['track']['release']))
    track_id = cur.fetchone()[0]
    fields = ['track_id', 'sequence', 'description']
    block['track_id'] = track_id
    cur.execute(insert_into('blocks', fields),
            [block[field] for field in fields])


def add_exercise(exercise, cur):
    cur.execute(
        "SELECT id FROM tracks WHERE sequence = %s AND release = %s;",
        (exercise['track']['sequence'], exercise['track']['release']))
    track_id = cur.fetchone()[0]
    cur.execute(
        "SELECT id FROM blocks WHERE track_id = %s AND sequence = %s",
        (track_id, exercise['track']['block']))
    block_id = cur.fetchone()[0]
    if 'moves' in exercise:
        moves = exercise['moves']
    else:
        moves = [{'description': exercise['description'],
                  'count': exercise['count']}]
        exercise['description'] = ""
    fields = ['block_id', 'description', 'reps', 'gear', 'start_time']
    exercise['block_id'] = block_id
    cur.execute(
            insert_into('exercises', fields)[:-1] + " RETURNING id;",
            [exercise[field] for field in fields])
    exercise_id = cur.fetchone()[0]
    move_fields = ['exercise_id', 'description', 'count', 'sequence']
    seq = int_seq()
    for move in moves:
        move['exercise_id'] = exercise_id
        move['sequence'] = next(seq)
        cur.execute(insert_into('moves', move_fields),
            [move[field] for field in move_fields])


def add_target(target, cur):
    fields = ['name']
    cur.execute(insert_into('targets', fields),
            [target[field] for field in fields])


def add_move_target(move_target, cur):
    cur.execute("SELECT id FROM targets WHERE name = %s;",
            (move_target['target'],))
    target_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM moves WHERE description LIKE %s;",
            ('%' + move_target['move'] + '%',))
    id_pairs = [(target_id, move[0]) for move in cur]
    for id_pair in id_pairs:
        cur.execute(
            insert_into('move_target', ['target_id', 'move_id']),
            id_pair)


def store_data(data_file=seeds):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    try:
        print "Loading seeds file %s" % (data_file, )
        data = json.load(open(data_file))
        for track in data['tracks']:
            add_track(track, cur)
        for block in data['blocks']:
            add_block(block, cur)
        for exercise in data['exercises']:
            add_exercise(exercise, cur)
        for target in data['targets']:
            add_target(target, cur)
        for move_target in data['exercise_targets']:
            add_move_target(move_target, cur)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def init_tables():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    try:
        cur.execute("DROP TABLE IF EXISTS {0};".format(
                commas(['tracks', 'exercises', 'targets', 'move_target',
                    'blocks', 'moves'])))
        cur.execute(open(init).read())
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    init_tables()
    store_data()
