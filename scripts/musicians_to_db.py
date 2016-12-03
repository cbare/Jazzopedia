"""
Read JSON scrapped from jazzdisco.org and populate tables
for groups and individuals

usage:
sqlite> .read ../scripts/drop_tables.sql
sqlite> .read ../scripts/create_tables.sql
$ python scripts/musicians_to_db.py
"""
import json
import os
import sqlite3
import re
from collections import Counter

from jazzdisco.utils import process_personnel
from utils import slugify

data_dir = '/Users/CBare/Documents/projects/jazz_discography/data'
filename = 'jazz.sqlite'
path = os.path.join(data_dir, filename)

person_fields = [
    'name', 'full_name', 'slug',
    'birth_date', 'birth_place', 'death_date', 'death_place']

## We'll use instruments to help differentiate between groups and
## individuals
with open('data/instruments.txt') as f:
    instruments = f.read().strip().split('\n')
instruments.append('female vocals')

with sqlite3.connect(path) as conn:
    c = conn.cursor()

    musicians = set()
    with open('data/jazzdiscography.json') as f:
        for line in f:
            d = json.loads(line)
            if 'roles' in d:
                ## separate groups from individuals
                if d['birth_date'] is None and all(role not in instruments for role in d['roles']):
                    query = 'INSERT INTO `Group` (name, description, slug) VALUES (?,?,?)'
                    c.execute(query, [d['name'], d['roles'][0], d['slug']])
                else:
                    query = 'INSERT INTO Person ({flds}) VALUES ({prms})'\
                            .format(flds=','.join(field for field in person_fields if field in d),
                                    prms=(','.join('?' for field in person_fields if field in d)))
                    c.execute(query, [d[field] for field in person_fields if field in d])
                    musicians.add(d['name'])

    cats = set()
    with open('data/unique_sessions.json') as f:
        for line in f:
            s = json.loads(line)
            for part in s['parts']:
                for pair in process_personnel(part['personnel']):
                    name = re.sub('^(possibly|probably) ', '', pair[0])
                    if ' or ' in name:
                        names = name.split(' or ')
                        for name in names:
                            if name == '"Little" Jimmy Scott': name = 'Little Jimmy Scott'
                            cats.add(name)
                    elif ' aka ' in name:
                        name = name.split(' aka ')[0]
                        cats.add(name)
                    else:
                        cats.add(name)

    cats = cats - musicians
    print('cats:', len(cats))

    for name in cats:
        c.execute('INSERT INTO Person (name, slug) VALUES (?, ?);', [name, slugify(name)])

    ## add records for identically named people
    c.execute('INSERT INTO Person (name, full_name, slug, birth_date, birth_place) VALUES (?,?,?,?,?);',
              ['Bill Evans', 'William D. Evans', 'bill-evans-sax', 'February 9, 1958', 'Clarendon Hills, IL'])

    c.execute('SELECT count(*) FROM Person;')
    n = c.fetchone()[0]
    print('count of persons = ', n)

    c.execute('select count(*) from Person where name like \'% as %\';')
    n = c.fetchone()[0]
    print('as (should be zero) ', n)

    print('Likely duplicates:')
    results = c.execute('select p1.name, p2.name from Person p1 join Person p2 where p1.slug==p2.slug and p1.id < p2.id order by p1.slug;')
    for result in results:
        print(result)

