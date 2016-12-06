import json
import os
import sqlite3
import time
from collections import defaultdict
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from utils import slugify
from io import StringIO
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)

## sqlite db
data_dir = '/Users/CBare/Documents/projects/jazz_discography/data'
filename = 'jazz.sqlite'
path = os.path.join(data_dir, filename)

def dict_factory(cursor, row):
    return {col[0]:row[idx] for idx, col in enumerate(cursor.description)}

@app.before_request
def before_request():
    ## for rough render time; see https://gist.github.com/lost-theory/4521102
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)

@app.route("/")
def hello():
    return render_template('home.html')

# @app.route("/album/<string:slug>")
# def album(slug):
#     return str(albums.get(slug, '"%s" not found'%slug))

# def by_session_id(s):
#     return s['session_id']

@app.route("/<string:slug>/")
def person(slug):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.row_factory = dict_factory
        c.execute('SELECT * FROM Person WHERE slug=?', [slug])
        m = c.fetchone()
        if m:
            results = c.execute('SELECT source,url FROM Data_Source WHERE entity_id=? AND entity_type="Person" ORDER BY source;', [m['id']])
            links = []
            for result in results:
                links.append(result)

            if m['birth_date'] and m['death_date']:
                m['age'] = relativedelta(parse(m['death_date']), parse(m['birth_date'])).years
                birth_death = ' - <i>b</i> {birth_date}, {birth_place}; <i>d</i> {death_date}, {death_place}; aged {age} '\
                                .format(**m)
            elif m['birth_date'] and not m['death_date']:
                m['age'] = relativedelta(datetime.now(), parse(m['birth_date'])).years
                birth_death = ' - <i>b</i> {birth_date}, {birth_place}; age {age} '\
                                .format(**m)
            else:
                birth_death = ''
            return render_template('musician.html', m=m, birth_death=birth_death, links=links)
        else:
            return '"%s" not found'%slug

@app.route("/group/<string:slug>/")
def group(slug):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.row_factory = dict_factory
        c.execute('SELECT * FROM `Group` WHERE slug=?', [slug])
        g = c.fetchone()
        if g:
            return render_template('group.html', g=g)
        else:
            return '"%s" not found'%slug

@app.route("/<string:slug>/sessions/")
def sessions(slug):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.row_factory = dict_factory

        c.execute('SELECT * FROM Person WHERE slug=?', [slug])
        person = c.fetchone()
        if person:
            query = """ select s.*
                        from Session s
                        join Person_Session ps on s.id=ps.session_id
                        where ps.person_id=?
                        order by s.jd_sort_key;"""

            ## retrieve sessions
            sessions = []
            results = c.execute(query, [person['id']])
            for result in results:
                sessions.append(result)

            for session in sessions:
                results = c.execute('select * from Part p where p.session_id=? order by sort_order', [session['id']])
                session['parts'] = []
                for result in results:
                    session['parts'].append(result)

            for session in sessions:
                for part in session['parts']:
                    results = c.execute('select * from Track t where t.part_id=? order by sort_order', [part['id']])
                    part['tracks'] = []
                    for result in results:
                        part['tracks'].append(result)

            return render_template('sessions.html', person=person, sessions=sessions)
        else:
            return '"%s" not found'%slug


if __name__ == "__main__":
    app.run(debug=True, use_debugger=True, use_reloader=True)
