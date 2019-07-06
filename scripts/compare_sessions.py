import json
from collections import Counter, defaultdict
from itertools import combinations


def make_key(d):
    return (d['group'],) + tuple(part['date'] for part in d['parts'] if part['date'])

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
        unique_sessions.append(us)
    else:
        unmerged_keys.append(k)

print('sessions:', len(sessions))
print('merged keys:', len(unique_sessions))
print('unmerged:', len(unmerged_keys))
