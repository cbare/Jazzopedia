"""
Find unique sessions in the JSON scraped from jazzdisco.org merging
different views of the same session when necessary and leaving some
sessions unmerged to be fixed up by hand.
"""
import json, re
from collections import Counter, defaultdict
from itertools import combinations
from utils import slugify


MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

def make_key(d):
    return (d['group'],) + tuple(part['date'] for part in d['parts'] if part['date'])

def extract_date(d):
    d =  set(part['date'] for part in d['parts'] if part['date'])
    if len(d) != 1:
        raise RuntimeError('session doesn\'t have exactly one date')
    return d.pop()

def split_location_date(d):
    """
    Separate a session description into a tuple of location and date.

    Typically, a session description looks something like this:
    "Columbia 30th Street Studios, NYC, March 2, 1959"

    But, there are lots of variants, which we try to deal with here.

    For example, Jazzdisco.org uses a variety of imprecise date forms
    such as, "fall 2006" or "circa late 1946-early 1947???".

    The first regex matches 23864 out of 26722 sessions. The second,
    matches another 2769.
    """
    m = re.match(r'(?:(.+),\s+)?(((originally\s+)?released\s+)?((circa|around)\s+)?(January|February|March|April|May|June|July|August|September|October|November|December).*)', d)
    if m:
        return m.group(1), m.group(2)

    m = re.match(r'(?:(.+),\s+)?(((originally\s+)?released\s+)?(possibly\s+)?(probably\s+)?(maybe\s+)?(between\s+)?((circa|around)\s+)?(before\s+)?((early|mid|late)\s+)?((spring|summer|fall|winter)\s+)?((19|20)\d\d)((-|\s+or\s+|\s+&\s+)(19|20)\d\d)*s?\?*)\s*$', d)
    if m:
        return m.group(1), m.group(2)

    ## circa late 1946-early 1947???
    ## fall 2006 & spring 2007
    m = re.match(r'(?:(.+),\s+)?((probably\s+)?(maybe\s+)?(between\s+)?(circa\s+)?((early|mid|late)\s+)?((spring|summer|fall|winter)\s+)?((19|20)\d\d)s?\?*(\s*(-|or|&)\s*)((early|mid|late)\s+)?((spring|summer|fall|winter)\s+)?((19|20)\d\d)s?\?*)\s*$', d)
    if m:
        return m.group(1), m.group(2)

    ##  late 1961 or early 1962
    ##  circa late 1947-early 1948???
    ##  late 1958-early 1959
    ##  early-mid 1967
    m = re.match(r'(?:(.+),\s+)?((probably\s+)?(maybe\s+)?(between\s+)?(circa\s+)?(early|mid|late|spring|summer|fall|winter)?(\s*(-|or|&)\s*)((early|mid|late)\s+)?((spring|summer|fall|winter)\s+)?((19|20)\d\d)s?\?*)\s*$', d)
    if m:
        return m.group(1), m.group(2)

    ## remaining special cases
    if d == 'unknown location, date':
        return None, None
    if d == 'NYC, probably October or late 1957 or 1958':
        return 'NYC', 'probably October or late 1957 or 1958'
    if d == 'Studio S4 Polskie Radio, Warsaw, Poland;<br/>released 2001':
        return 'Studio S4 Polskie Radio, Warsaw, Poland', 'released 2001'
    m = re.match(r'(.+),\s+unknown date', d)
    if m:
        return m.group(1), None
    return None, None

def compare_tracks(s1, s2):
    tr1 = set(t['name'] for p in s1['parts'] for t in p['tracks'])
    tr2 = set(t['name'] for p in s2['parts'] for t in p['tracks'])
    if tr1 == tr2:
        return 0
    elif tr1 <= tr2:
        return -1
    elif tr1 >= tr2:
        return 1
    else:
        return 999

def session_superset_or_none(ds):
    for d1 in ds:
        if all(compare_tracks(d1,d2) in [0,1] for d2 in ds):
            return d1
    else:
        return None

def merge(ds):
    result = {k:v for k,v in ds[0].items() if k != 'parts'}
    parts = []
    for d in ds:
        for k,v in d.items():
            if k != 'parts':
                print(d[k], '==' if d[k]==result[k] else '!=', result[k])
        parts.append(d['parts'])
    result['parts'] = parts
    return result


sessions = defaultdict(list)
with open('data/jazzdiscography.json') as f:
    for line in f:
        d = json.loads(line)
        if 'session_id' in d:
            sessions[make_key(d)].append(d)

            ## add source url to session JSON
            slug = slugify(d['catalog_source'])
            url = 'http://jazzdisco.org/{slug}/discography#{session_id}'.format(slug=slug, session_id=d['session_id'])
            d['source_url'] = url

with open('data/label_data_jazzdisco.json') as f:
    for line in f:
        d = json.loads(line)
        if 'session_id' in d:
            sessions[make_key(d)].append(d)

unique_sessions = []
unmerged_keys = []
for k,v in sessions.items():
    us = session_superset_or_none(v)
    if us is not None:
        us['source_urls'] = [(session['catalog_source'], session['source_url']) for session in v]
        unique_sessions.append(us)
    else:
        unmerged_keys.append(k)

## merge in manually repaired sessions
with open('data/sessions_fixed.py') as f:
    exec(f.read())
unique_sessions += fixed_sessions
unmerged_keys = [k for k in unmerged_keys if k not in fixed_session_keys]

for session in unique_sessions:
    if 'source_urls' not in session:
        print(session)
        raise RuntimeError("All sessions should have source urls")

## for the remaining unmerged sessions, just throw them in
for key in unmerged_keys:
    for session in sessions[key]:
        session['source_urls'] = [(session['catalog_source'], session['source_url']+'#'+session['session_id'])]
        unique_sessions.append(session)

print('sessions:', len(sessions))
print('merged keys:', len(unique_sessions))

for session in unique_sessions:
    place, date = split_location_date(extract_date(session))
    session['date'] = date
    session['place'] = place

    ## update the sort keys to contain 19 for century so they sort
    ## properly with 21st century sort keys (that start with 20)
    m = re.match(r'^\d{6}(-.*)?$', session['session_id'])
    if m:
        session['session_id'] = '19' + session['session_id']

print('unique sessions:', len(unique_sessions))

with open('data/unique_sessions.json', 'w') as f:
    for session in unique_sessions:
        f.write(json.dumps(session))
        f.write("\n")

