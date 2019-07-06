"""
Match up albums from artist catalogs and from session notes
"""
import html
import json
import os
import sqlite3
import re
from collections import Counter, defaultdict
from jazzdisco.utils import same
from tools import hist


## read in albums associated with musician catalogs
albums = defaultdict(list)
albums_by_id = defaultdict(list)
with open('data/jazzdiscography.json') as f:
    for line in f:
        d = json.loads(line)
        if 'title' in d and 'parts' in d:
            albums[(d['artist'], d['title'])].append(d)
            albums_by_id[d['catalog_number']].append(d)

print('histogram of matching album artist and titles:')
print(hist(len(v) for k,v in albums.items()))

## read sessions from sqlite db
data_dir = '/Users/CBare/Documents/projects/jazz_discography/data'
filename = 'jazz.sqlite'
path = os.path.join(data_dir, filename)

with sqlite3.connect(path) as conn:
    c = conn.cursor()
    results = c.execute('SELECT * FROM Session ORDER BY id;')    
    sessions = list(results)

## find albums associated with sessions
albums_sessions = []
for session in sessions:
    items = session[5].split("<br/>\n")
    session_id = session[0]
    for item in items:
        if item:
            albums_sessions.append((item.strip(), session_id))

## parse album artist / title / catalog number
session_albums_by_id = defaultdict(list)
session_albums = defaultdict(list)
for item, session_id in albums_sessions:
    artist = None
    m = re.match(r'[*=] (.+?(?:; .+?)*) \xa0 <i>(.+)</i>', item)
    if m:
        ## the albums titles are extracted using beautiful soup's element.string
        ## which decodes them html. Here we're using the markup to help parse out
        ## the catalog number and album title, so it's not decoded. We have to be
        ## Carefule to decode after splitting the session album info into fields.
        cat_nums = html.unescape(m.group(1))
        title = html.unescape(m.group(2))
        fields = re.split(r' - ', title)
        if len(fields) == 2:
            artist, title = fields

        album = {
            "title":title,
            "artist":artist,
            "catalog_ids":cat_nums,
            "session_id":session_id}
        session_albums[(artist,title)].append(album)

        for catalog_id in re.split(r';\s+', cat_nums):
            session_albums_by_id[catalog_id].append(album)
    else:
        raise RuntimeError('can\'t parse: {item}'.format(item=item))

## QA: show albums for which we can't 
common_keys = set(session_albums.keys()) & set(albums.keys())
print("fraction of catalog albums also found in sessions: %.4f"%(len(common_keys)/len(albums)))
print("fraction of session albums also found in catalogs: %.4f"%(len(common_keys)/len(session_albums)))

if len(common_keys) > 0 and len(common_keys) < 200:
    print("Albums with no linked sessions:")
    for item in (set(albums.keys()) - set(session_albums.keys())):
        print(item)


## jazzdisco expresses catalog numbers in a confusing variety of
## forms. Also, the labels often release the same album under
## different numbers or even release under different labels.
## See Original Jazz Classics:
##   https://en.wikipedia.org/wiki/Original_Jazz_Classics

n = sum(key in session_albums_by_id for key in albums_by_id.keys())
print("Catalog numbers found in albums and sessions:", n)

n = sum(key not in session_albums_by_id for key in albums_by_id.keys())
print("Catalog numbers found in albums but not in sessions:", n)

## Examples:
# ['Landmark LCD-1516-2', 'Landmark LLP-1516']
# ['Original Jazz Classics OJCCD-1792-2', 'Riverside RLP 12-302']
# ['SteepleChase (D) SCCD-31023', 'SteepleChase (D) SCS-1023']
# ['Blue Note BLP 4260', 'Blue Note CDP 7 84260 2']
# ['Blue Note B1-93598', 'Blue Note CDP 7 93598 2']
# ['Verve (J) J28J-25115', 'Verve MGV 8198']
# ['ECM (G) ECM 1419', 'ECM (G) ECM 1419 (CD)']

## Here we're looking for albums with the same artist and title
## but different catalog numbers

## count non-matching catalog numbers
n = sum(not same(d['catalog_number'] for d in v) for k,v in albums.items())
print("albums with non-matching catalog numbers: {} out of {}.".format(n,len(albums)))

## Many or most of these seem to be variations of the same catalog number. I don't want
## to get caught up in worrying about cannonical forms of label catalog numbers. Discogs
## already does that way better than I have any interest in doing. If I can link each
## album to its master entry in Discogs, that'll be fine.

## find non-matching catalog numbers
# for k,v in albums.items():
#     if len(v) > 1:
#         if not same(d['catalog_number'] for d in v):
#             print(sorted(set(d['catalog_number'] for d in v)))


def tuple_sort_key(t):
    """
    Sort key for tuples of ({artist}, {title}) where artist may
    be None
    """
    return tuple("" if a is None else a for a in t)

## Write albums to SQLite
with sqlite3.connect(path) as conn:
    c = conn.cursor()

    keys = sorted(session_albums.keys(), key=tuple_sort_key)
    for key in keys:
        artist, title = key

        ## TODO: Better parsing of catalog numbers needed here!

        if key in albums:
            catalog_numbers = set(album['catalog_number'] for album in albums[key])
            notes = "<br/>\n".join(set(album['notes'] for album in albums[key]))
        else:
            catalog_numbers = set()
            notes = None

        note = notes or None

        session_ids = []
        for album in session_albums[key]:
            session_ids.append(album['session_id'])
            catalog_numbers.update(re.split(r'; ', album['catalog_ids']))

        c.execute('INSERT INTO Album '\
                  '(artist, title, artist_in_title, notes) values (?,?,?,?);',
                  [artist, title, artist is None, notes])
        album_id = c.lastrowid

        ## TODO: Separate out label and catalog number(s)
        for catalog_number in catalog_numbers:
            c.execute('INSERT INTO Album_Catalog_Number (album_id, catalog_number) values (?,?);',
                      [album_id, catalog_number])

        for session_id in session_ids:
            c.execute('INSERT INTO Album_Session (album_id, session_id) values (?,?);',
                      [album_id, session_id])

        if key in albums:
            for album in albums[key]:
                query = 'INSERT INTO Data_Source (entity_id, entity_type, source, url, data_quality) '\
                        'VALUES (?,"Album",?,?,"unverified")'
                c.execute(query, [album_id,
                                  "Jazz Discography Project ({catalog_source} catalog)".format(catalog_source=album['catalog_source']),
                                  album['source_url']+"#"+album['catalog_slug']])


with sqlite3.connect(path) as conn:
    c = conn.cursor()

    q = """\
        select distinct catalog_number
        from Album_Catalog_Number
        order by catalog_number;
        """

    catnos = [row[0] for row in c.execute(q)]


regexes = [
    r'([A-Z]?[a-z]+(?:!|\'|\'s)?(?:[\- ][A-Z]?[a-z]+(?:!|\.|\'|\'s)?)*)(?: \((\w+)\))? ([A-Z0-9]+(?:[\- ./][A-Z0-9]+)*(?:x45|/\d+)?)\?*(?: \(|, |$)',
    r'([A-Z][a-z]+(?:[\- ][A-Z]?[a-z]+)*)(?: \((\w+)\))? (?:Criss|Jass|MUS.) ([A-Z0-9]+(?:[\- ./][A-Z0-9]+)*(?:x45|/\d+)?)\?*(?: \(|, |$)',
    r'([A-Z][a-z]+(?: & |/)[A-Z][a-z]+)(?: \((\w+)\))? ([A-Z0-9]+(?:[\- ./][A-Z0-9]+)*(?:x45|/\d+)?)\?*(?: \(|, |$)',
    r'([A-Z][a-z]+[A-Z][a-z]+(?: [A-Z][a-z]+)*)(?: \((\w+)\))? ([A-Z0-9]+(?:[\- ./][A-Z0-9]+)*(?:x45|/\d+)?)\?*(?: \(|, |$)',
    r'([A-Z]&[A-Z])(?: \((\w+)\))? ([A-Z0-9]+(?:[\- ./][A-Z0-9]+)*(?:x45|/\d+)?)\?*(?: \(|, |$)',
    r'(\d+[a-z]*(?: [A-Z][a-z]+)*)(?: \((\w+)\))? ([A-Z0-9]+(?:[\- ./][A-Z0-9]+)*(?:x45|/\d+)?)\?*(?: \(|, |$)',
    r'([A-Z]{1,5}(?:[\- /][A-Z][a-z]+(?:\'|\'s)?)+)(?: \((\w+)\))? ([A-Z0-9]+(?:[\- ./][A-Z0-9]+)*(?:x45|/\d+)?)\?*(?: \(|, |$)',
    r'([A-Z]{2,6})(?: \((\w+)\))? (?::rarum )?([A-Z0-9]+(?:[\- ./][A-Z0-9]+)*(?:x45|/\d+)?)\?*(?: \(|, |$)',
    r'([A-Za-z0-9]{2,50}(?:[\- ][A-Z][a-z]+)*)(?: \((\w+)\))? ([A-Z0-9]+(?:[\- ./][A-Z0-9]+)*(?:x45|/\d+)?)\?*(?: \(|, |$)',
    r'((?:[A-Z]\.){2,8}(?:[\- ][A-Z][a-z]+)*)(?: \((\w+)\))? ([A-Z0-9]+(?:[\- ./][A-Z0-9]+)*(?:x45|/\d+)?)\?*(?: \(|, |$)']

remaining = list(catnos)
labels = set()
print(len(remaining))
for regex in regexes:
    nomatch = []
    for catno in remaining:
        if catno:
            m = re.match(regex, catno)
            if m:
                labels.add(m.group(1))
            else:
                nomatch.append(catno)
    remaining = nomatch
    print(len(remaining))

## add in hard-to-parse label names
labels.update([
    '18th & Vine', '3361*Black', 'A&M/Horizon', 'Altus/NHK CD',
    'AFRS Transcription', 'Arista/GRP', "Aketa's Disk",
    'Ark 21 Records', 'Bang & Olufsen', 'BE! Jazz', 'CBS/Associated',
    'CBS/Sony', 'CIMP', 'CTI/Associated', 'Columbia/ARC',
    'Crane River Jazz', 'Cool & Blue', 'Decca',
    "Disc'Az", 'Dr. Jazz', 'E.S.Tee Recordings', "ELM/ESP-Disk'",
    'EMI/Electrola', 'EP/Visom Digital', 'Fabbri Editori',
    'GNP/ZYX', 'Gryphon Productions, Inc.', 'IN+OUT Records',
    'Ingo', 'Island/Guts & Grace', 'Intakt Records',
    'J-V-B', 'Jass Records', 'Jazz Road/Apollon', 'Jazz O.P.',
    "Jazz Birdie's Of Paradise Best.-Nr.", "Jazz'N'Arts",
    'Jazzwerkstatt', 'Jazzpoint', 'Just A Memory', "Key'stone",
    'L+R', 'Latin Jazz & Dance Records', "Live At E.J.'s", 'LRC Ltd.',
    "Luv N' Haight", 'Mah/Meta Records', 'MGM/Lion', 'MPS/BASF',
    'Mercury', 'Moers Music', 'Menus And Music Productions, Inc.',
    'Nagara', 'Naim Label', 'Naxos', 'NEC Avenue, Ltd.', 'No Blooze Music',
    "O'Be Records", 'Polonia Records', 'Sagittarius A-Star',
    'PAN TAU-X Records', 'Rhino/Warner Bros.', 'Ring Records',
    'PJL/Jazzbank', 'Point', 'RCA "X"', 'Solid/enja', 'Stomp Off',
    'T-TOC Records', 'World McC Music', 'Weka',
    'Tokyo M-Plus', 'Top Jazz', 'XtraWATT', 'The ACT Company',
    'veraBra Records', 'Victo',
    'V.S.O.P.', 'VGM/Soulard', 'Whiskey, Women And...', "somethin'else"])

nomatch = []
for catno in remaining:
    for label in labels:
        if catno.startswith(label):
            break
    else:
        nomatch.append(catno)
remaining = nomatch
print(len(remaining))


with open('data/jazzdisco_labels.txt', 'w') as f:
    for label in sorted(labels):
        f.write(label)
        f.write('\n')

