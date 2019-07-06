import json
from collections import defaultdict
from utils import process_personnel

musicians = {}
with open('data/jazzdiscography.json') as f:
    for line in f:
        d = json.loads(line)
        if 'roles' in d:
            musicians[d['name']] = d

sessions = []
with open('data/unique_sessions.json') as f:
    for line in f:
        d = json.loads(line)
        sessions.append(d)
print(len(sessions))

links = defaultdict(list)
for session in sessions:
    for part in session['parts']:
        for name, role in process_personnel(part['personnel']):
            links[name].append((name, role, session, part))

def by_session_id(s):
    return s[2]['session_id']

for link in sorted(links['Paul Chambers'], key=by_session_id):
    print('-'*60)
    print(link[0], link[1], link[2]['group'])
    print(link[2]['place'], link[2]['date'])
    print(link[3]['personnel'])
    for track in link[3]['tracks']:
        print(track['id'], track['name'], track['issued'])
    print(link[2]['notes'])

