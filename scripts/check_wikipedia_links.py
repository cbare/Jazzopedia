import re
import requests
import bs4
import time

skip = True
with open('data/wikipedia_links.txt') as f:
    for line in f:
        name, url = line.strip().split(',  ')
        if skip:
            print('skipping', name)
            if name == 'John Patton':
                skip = False
            continue
        response = requests.get(url)
        if response.status_code >= 200 and response.status_code < 300:
            html = response.text
            soup = bs4.BeautifulSoup(html, 'lxml')

            ## Names suck as a way of uniquely identifying people.

            ## Some Wikipedia disambiguation pages have disambiguation
            ## in their title. Many contain the text "may refer to:",
            ## but neither of these can be relied on.
            if 'disambiguation' in soup.title.text or 'may refer to:' in soup.body.text:
                print(name, url, 'disambiguation')

            ## This will erroneously pass pages that link to alternate
            ## people of the same name, for a example (in the opposite direction):
            ## https://en.wikipedia.org/wiki/John_Levy_(musician)
            elif 'jazz' in soup.body.text or 'musician' in soup.body.text or 'singer' in soup.body.text:
                pass #print(name, url, 'ok')

            ## These pages are usually someone else of the same name
            else:
                print(name, url, '??')
        else:
            print(name, url, 'XXX')
        time.sleep(1)
