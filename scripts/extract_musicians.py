import json
from collections import Counter
from itertools import combinations
from utils import process_personnel


roles = Counter()
musicians = {}
peeps = set()
musician_roles = set()

with open('data/jazzdiscography.json') as f:
    for line in f:
        d = json.loads(line)
        if 'roles' in d:
            musicians[d['slug']] = d
            for role in d['roles']:
                musician_roles.add(role)
        elif 'title' in d and 'parts' in d:
            for part in d['parts']:
                for pair in process_personnel(part['personnel']):
                    roles[pair] += 1
                    peeps.add(pair[0])
        elif 'session_id' in d and 'parts' in d:
             for part in d['parts']:
                for pair in process_personnel(part['personnel']):
                    roles[pair] += 1
                    peeps.add(pair[0])
        else:
            raise RuntimeError('huh? What was that:\n' + line)

def sort_key(role_count):
    return role_count[1], role_count[0]

print('musicians:', len(musicians))
print('musician roles:', len(musician_roles))
print('peeps:', len(peeps))

print('musician_roles', musician_roles)

musician_names = set(musician['name'] for musician in musicians.values())

print('roles:', sum(cnt for key,cnt in roles.items()))
roles = sorted(roles.items(), key=sort_key, reverse=True)
for role in roles:
    print(role[0][0], role[0][1], role[1], role[0][0] in musician_names)

for p in sorted(peeps):
    print(p)

