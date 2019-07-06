import json
import os
import sqlite3
import re
from collections import Counter

c_matches = 0
c_nonmatches = 0

with open('data/unique_sessions.json') as f:
    for line in f:
        s = json.loads(line)
        notes = s['notes']

        lines = notes.split('<br/>')

        print('-'*70)
        for line in lines:
            line = line.strip()
            m = re.match(r'(\*|=) (.*)   <i>(?:(.+) - )?(.+)<\/i>', line)
            if m:
                c_matches += 1
                # print(m.group(1), m.group(2), m.group(3), m.group(4))
            else:
                c_nonmatches += 1

            print("====>", c_matches, c_nonmatches)
            print(line)
