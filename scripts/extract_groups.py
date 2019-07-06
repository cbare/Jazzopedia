import json
from collections import Counter
from itertools import combinations
from utils import process_personnel


musicians = {}
groups = {}

with open('data/instruments.txt') as f:
    instruments = f.read().strip().split('\n')

instruments.append('female vocals')

with open('data/jazzdiscography.json') as f:
    for line in f:
        d = json.loads(line)
        if 'roles' in d:
            if d['birth_date'] is None and all(role not in instruments for role in d['roles']):
                print(d['name'], d['slug'], d['roles'])
            else:
                pass #print(d['name'], d['slug'], d['roles'])
