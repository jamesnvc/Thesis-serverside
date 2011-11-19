#!/usr/bin/env python2.7
import os
import json
import psycopg2

seeds = os.path.join(os.path.dirname(__file__), '..', 'seeds.json')
init = os.path.join(os.path.dirname(__file__), '..', 'db_init.sql')
conn = psycopg2.connect("dbname=musashi-dev user=tester")
cur = conn.cursor()


def insert_into(table, fields):
    commas = ', '.join
    return "INSERT INTO {0} ({1}) VALUES ({2})".format(
        table, commas(fields), commas(['%s']*len(fields)))

def add_track(track):
    fields = ["sequence", "release", "exercise", "count", "reps",
            "intensity", "song"]
    cur.execute(
            insert_into('tracks', fields),
            [track[field] for field in fields])


def store_data(data_file=seeds):
    data = json.loads(open(data_file))
    for track in data['tracks']:
        add_track(track)

def init_tables():
    cur.execute(open(init).read())
