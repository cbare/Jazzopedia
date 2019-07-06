from lxml import etree
import sys

names = []

jazz = ["Miles Davis", "John Coltrane", "Bill Evans", "Paul Chambers (3)", "Cannonball Adderley",
        "Lee Konitz", "Lennie Tristano", "McCoy Tyner", "Elvin Jones", "Keith Jarrett"]


doc = etree.parse('/Users/CBare/Documents/projects/jazz_discography/data/discogs_20161101_artists.xml')

i = 0
for node in doc.xpath('/artists/artist'):
    x = etree.tostring(node, pretty_print=True, encoding="utf-8").decode('utf-8')
    name = ''.join(node.xpath('name')[0].itertext())
    if name in jazz:
        print(etree.tostring(node, pretty_print=True, encoding='utf-8').decode('utf-8'))
    names.append(name)

print("artists:", len(names))

print("----------"*6)

for name in names[:100]:
    print(name)

print("----------"*6)

