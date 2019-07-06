import re
import requests

with open('out.txt') as f:
    for line in f:
        name = line.split(', ')[0]
        url = 'https://en.wikipedia.org/wiki/' + re.sub(r'[\'"]', '', re.sub(r'[ -]', '_', name))
        response = requests.head(url)
        if response.status_code >= 200 and response.status_code < 300:
            print(name, ', ', url)
        else:
            print(name, ', XXX')
