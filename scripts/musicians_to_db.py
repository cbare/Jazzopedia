"""
Read JSON scrapped from jazzdisco.org and populate tables
for groups and individuals

usage:
sqlite> .read ../scripts/drop_tables.sql
sqlite> .read ../scripts/create_tables.sql
$ python scripts/musicians_to_db.py
"""
import json
import os, sys
import sqlite3
import re
from collections import Counter, defaultdict

from jazzdisco.utils import process_personnel
from utils import slugify

data_dir = '/Users/CBare/Documents/projects/jazz_discography/data'
filename = 'jazz.sqlite'
path = os.path.join(data_dir, filename)

person_fields = [
    'name', 'full_name', 'slug',
    'birth_date', 'birth_place', 'death_date', 'death_place']


def fixup_pairs(pair_iterator):
    for pair in pair_iterator:
        name = re.sub('^(possibly|probably) ', '', pair[0])
        role = pair[1]
        if ' or ' in name:
            names = name.split(' or ')
            for name in names:
                ## a hack to handle: probably Chubby Newsome or "Little" Jimmy Scott
                ## which is an entry in the Fats Navarro discography
                if name == '"Little" Jimmy Scott': name = 'Little Jimmy Scott'
                yield (name,role)
        elif ' aka ' in name:
            name = name.split(' aka ')[0]
            yield (name,role)
        else:
            yield (name,role)


## We'll use instruments to help differentiate between groups and
## individuals
with open('data/instruments.txt') as f:
    instruments = f.read().strip().split('\n')
instruments.append('female vocals')

with sqlite3.connect(path) as conn:
    c = conn.cursor()

    ## import data for jazzdisco featured musicians
    musicians = {}
    with open('data/jazzdiscography.json') as f:
        for line in f:
            d = json.loads(line)
            if 'roles' in d:
                ## separate groups from individuals
                if d['birth_date'] is None and all(role not in instruments for role in d['roles']):
                    query = 'INSERT INTO `Group` (name, description, slug) VALUES (?,?,?)'
                    c.execute(query, [d['name'], d['roles'][0], d['slug']])
                    ## add data source
                    query = 'INSERT INTO Data_Source (entity_id, entity_type, source, url, data_quality)'\
                            ' VALUES (?,"Group","Jazz Discography Project",?,"Likely OK")'
                    c.execute(query, [c.lastrowid, "http://www.jazzdisco.org/"+d['slug']+"/"])
                else:
                    query = 'INSERT INTO Person ({flds}) VALUES ({prms})'\
                            .format(flds=','.join(field for field in person_fields if field in d),
                                    prms=(','.join('?' for field in person_fields if field in d)))
                    c.execute(query, [d[field] for field in person_fields if field in d])
                    musicians[d['name']] = c.lastrowid

                    ## add data source
                    query = 'INSERT INTO Data_Source (entity_id, entity_type, source, url, data_quality)'\
                            ' VALUES (?,"Person","Jazz Discography Project",?,"Likely OK")'
                    c.execute(query, [c.lastrowid, "http://www.jazzdisco.org/"+d['slug']+"/"])


    ## add records for identically named people
    c.execute('INSERT INTO Person (name, full_name, slug, birth_date, birth_place) VALUES (?,?,?,?,?);',
              ['Bill Evans', 'William D. Evans', 'bill-evans-sax', 'February 9, 1958', 'Clarendon Hills, IL'])
    bill_evans_sax_id = c.lastrowid

    ## add data source
    query = 'INSERT INTO Data_Source (entity_id, entity_type, source, url, data_quality) '\
            'VALUES (?,"Person","Discogs","https://www.discogs.com/artist/503619-Bill-Evans-3","verified")'
    c.execute(query, [c.lastrowid])


    ## collect unique names and sources from sessions
    cats = {k:v for k,v in musicians.items()}
    with open('data/unique_sessions.json') as f:
        for line in f:
            s = json.loads(line)

            c.execute('INSERT INTO Session (jd_sort_key, `group`, place, `date`, notes) values (?,?,?,?,?);',
                      [s['session_id'],
                       s['group'],
                       s['place'],
                       s['date'],
                       s['notes']])
            session_id = c.lastrowid

            ## add data sources
            if 'source_urls' in s:
                for catalog_source, url in s['source_urls']:
                    query = 'INSERT INTO Data_Source (entity_id, entity_type, source, url, data_quality) '\
                            'VALUES (?,"Session",?,?,"unverified")'
                    c.execute(query, [session_id,
                                      "Jazz Discography Project ({catalog_source} discography)".format(catalog_source=catalog_source),
                                      url])
            else:
                print(s)
                raise RuntimeError("all sessions should have source urls")

            part_order = 0
            for part in s['parts']:
                part_order += 1

                ## add part to db
                c.execute('INSERT INTO Part (sort_order, session_id, personnel) values (?,?,?);',
                          [part_order, session_id, part['personnel']])
                part_id = c.lastrowid
                track_order = 0
                for track in part['tracks']:
                    track_order += 1
                    c.execute('INSERT INTO Track (sort_order, part_id, name, issued, catalog_id) values (?,?,?,?,?);',
                              [track_order, part_id, track['name'], track['issued'] or None, track['id'] or None])

                ## extract musician - role pairs out of unstructured personnel lists
                for name, role in fixup_pairs(process_personnel(part['personnel'])):
                    if name in cats:
                        person_id = cats[name]
                        if name=='Bill Evans':
                            if any(instr in role.lower() for instr in ['sax', 'soprano', 'tenor', 'flute']):
                                person_id = bill_evans_sax_id
                    else:
                        c.execute('INSERT INTO Person (name, slug) VALUES (?, ?);', [name, slugify(name)])
                        person_id = c.lastrowid

                    cats[name] = person_id
                    c.execute('INSERT INTO Person_Part (person_id, part_id, role) values (?,?,?);',
                              [person_id, part_id, role])

    ## a little data quality control
    c.execute('SELECT count(*) FROM Person;')
    n = c.fetchone()[0]
    print('count of persons = ', n)

    c.execute('SELECT count(*) FROM Session;')
    n = c.fetchone()[0]
    print('count of sessions = ', n)

    c.execute('select count(*) from Person where name like \'% as %\';')
    n = c.fetchone()[0]
    print('as (should be zero) ', n)

    print('Likely duplicates:')
    results = c.execute('select p1.name, p2.name from Person p1 join Person p2 where p1.slug==p2.slug and p1.id < p2.id order by p1.slug;')
    for result in results:
        print(result)

