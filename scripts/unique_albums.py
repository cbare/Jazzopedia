import json
from collections import Counter, defaultdict
from itertools import combinations
import sqlite3
import re

roles = Counter()
musicians = {}
collabs = Counter()
sessions = {}
all_sessions = []


albums = set()
with open('data/jazzdiscography.json') as f:
    for line in f:
        d = json.loads(line)
        if 'title' in d and 'parts' in d:
            albums.add((d['artist'], d['title']))


## open sqlite db
data_dir = '/Users/CBare/Documents/projects/jazz_discography/data'
filename = 'jazz.sqlite'
path = os.path.join(data_dir, filename)

with sqlite3.connect(path) as conn:
    c = conn.cursor()
    results = c.execute('SELECT * FROM Session ORDER BY id;')    
    sessions = list(results)


## find albums associated with sessions
i = 0
albums_to_sessions = defaultdict(list)
for session in sessions:
    items = session[5].split("<br/>\n")
    for item in items:
        albums_to_sessions(item.strip()).append(session[0])
        i += 1

cm = 0
releases_by_catalog_id = defaultdict(list)
session_albums = defaultdict(list)
for item, session_ids in albums_to_sessions.items():
    if item == '': continue
    artist = None
    m = re.match(r'[*=] (.+?(?:; .+?)*) \xa0 <i>(.+)</i>', item)
    if m:
        title = m.group(2)
        m = re.match(r'[*=] (.+?(?:; .+?)*) \xa0 <i>(.+) - (.+) / (.+) - (.+)</i>', item)
        if m:
            artist = m.group(2) + ' / ' + m.group(4)
        else:
            m = re.match(r'[*=] (.+?(?:; .+?)*) \xa0 <i>(.+) - (.+)</i>', item)
            if m:
                artist = m.group(2)
                title = m.group(3)

        album = {
            "title":title,
            "artist":artist,
            "catalog_ids":re.split(r';\s+', m.group(1))}
        if len(m.group(2).split(' - ')) > 2:
            print(m.group(2))

        if ' - ' in m.group(2):
            artist, title = m.group(2).rsplit(' - ', 1)
        else:
            artist = None
            title  = m.group(2)
        session_albums.add(item)
        for catalog_id in catalog_ids:
            releases[catalog_id].append(catalog_id)
    else:
        raise RuntimeError('can\'t parse: {item}'.format(item=item))


c_split_single = 0
c_artist_title = 0
c_title_only   = 0
releases_by_catalog_id = defaultdict(list)
session_albums = defaultdict(list)
for session_id, item in unique_items:
    if item == '': continue
    m = re.match(r'[*=] (.+?(?:; .+?)*) \xa0 <i>(.+) - (.+) / (.+) - (.+)</i>', item)
    if m:
        c_split_single += 1
    else:
        m = re.match(r'[*=] (.+?(?:; .+?)*) \xa0 <i>(.+) - (.+)</i>', item)
        if m:
            c_artist_title += 1
        else:
            m = re.match(r'[*=] (.+?(?:; .+?)*) \xa0 <i>(.+)</i>', item)
            if m:
                c_title_only += 1
            else:
                raise RuntimeError('dammit!', item)
print('c_split_single', c_split_single)
print('c_artist_title', c_artist_title)
print('c_title_only',   c_title_only)

## check consistency of catalog_id <-> title pairings
## -- 34 mismatches out of 31742 unique albums
mm = 0
for key,vals in releases.items():
    prev = vals[0]
    for val in vals[1:]:
        if not prev==val:
            print(key,vals)
            mm += 1
print(mm, "mismatches")



print(i, 'items')
print(cm, 'matching items')
print(len(unique_items), 'unique items')
