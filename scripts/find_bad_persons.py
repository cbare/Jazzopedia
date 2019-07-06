import json
import os
import sqlite3
import re
from collections import Counter

from jazzdisco.utils import process_personnel
from utils import slugify

cats = set()
with open('data/unique_sessions.json') as f:
    for line in f:
        s = json.loads(line)
        for part in s['parts']:
            for pair in process_personnel(part['personnel']):
                name = re.sub('^(possibly|probably) ', '', pair[0])
                cats.add(name)

## all or nearly all lower case names are bad data, things like "string section"
print([cat for cat in cats if cat[0] >= 'a' and cat[0] <='z'])

