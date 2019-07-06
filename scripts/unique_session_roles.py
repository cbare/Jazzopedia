import json
from collections import Counter
from itertools import combinations
from utils import process_personnel


roles = Counter()
musicians = {}
peeps = set()

with open('data/jazzdiscography.json') as f:
    for line in f:
        d = json.loads(line)
        if 'roles' in d:
            musicians[d['slug']] = d

with open('data/unique_sessions.json') as f:
    for line in f:
        s = json.loads(line)
        session_roles = set()
        for part in s['parts']:
            for pair in process_personnel(part['personnel']):
                session_roles.add(pair)
                peeps.add(pair[0])
        for pair in session_roles:
            roles[pair[0]] += 1


def sort_key(role_count):
    return role_count[1], role_count[0]

print('musicians:', len(musicians))
print('peeps:', len(peeps))

musician_names = set(musician['name'] for musician in musicians.values())

print('roles:', sum(cnt for key,cnt in roles.items()))
roles = sorted(roles.items(), key=sort_key, reverse=True)
# for role in roles:
#     print(", ".join([role[0][0], role[0][1], str(role[1]), str(role[0][0] in musician_names)]))

for role in roles[:1000]:
    print(", ".join([role[0], str(role[1]), str(role[0] in musician_names)]))
