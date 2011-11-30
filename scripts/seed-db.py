#!/usr/bin/env python2.7
import os
import json
import psycopg2

seeds = os.path.join(os.path.dirname(__file__), '..', 'seeds.json')
init = os.path.join(os.path.dirname(__file__), '..', 'db_init.sql')
commas = ', '.join


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
    fields = ['block_id', 'description', 'count', 'reps', 'gear', 'start_time']
    exercise['block_id'] = block_id
    cur.execute(
            insert_into('exercises', fields),
            [exercise[field] for field in fields])


def add_target(target, cur):
    fields = ['name']
    cur.execute(insert_into('targets', fields),
            [target[field] for field in fields])


def add_exercise_target(exercise_target, cur):
    cur.execute("SELECT id FROM targets WHERE name = %s;",
            (exercise_target['target'],))
    target_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM exercises WHERE description LIKE %s;",
            ('%' + exercise_target['exercise'] + '%',))
    id_pairs = [(target_id, exercise[0]) for exercise in cur]
    for id_pair in id_pairs:
        cur.execute(
            insert_into('exercise_target', ['target_id', 'exercise_id']),
            id_pair)


def store_data(data_file=seeds):
    conn = psycopg2.connect("dbname=musashi-dev user=tester")
    cur = conn.cursor()
    try:
        data = json.load(open(data_file))
        for track in data['tracks']:
            add_track(track, cur)
        for block in data['blocks']:
            add_block(block, cur)
        for exercise in data['exercises']:
            add_exercise(exercise, cur)
        for target in data['targets']:
            add_target(target, cur)
        for exercise_target in data['exercise_targets']:
            add_exercise_target(exercise_target, cur)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def init_tables():
    conn = psycopg2.connect("dbname=musashi-dev user=tester")
    cur = conn.cursor()
    try:
        cur.execute("DROP TABLE IF EXISTS {0};".format(
                commas(['tracks', 'exercises', 'targets', 'exercise_target',
                    'blocks'])))
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