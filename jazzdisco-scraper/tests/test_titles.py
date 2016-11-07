from jazzdisco.utils import process_title

title_lines = """\
Wardell Gray Memorial, Vol. 1  (Prestige PRLP 7008)
Art Pepper With Sonny Clark Trio - Straight-Ahead Jazz, Vol. 1  (Straight-Ahead Jazz SAJ-1001)
The Sonny Clark Memorial Album  (Xanadu 121)
Jimmy Raney/Sonny Clark - Together  (Xanadu 209)
Howard Rumsey's Lighthouse All-Stars - Music For Lighthousekeeping  (Contemporary C 3528)
Dizzy Gillespie - Big Band Live In Hi-Fi From Birdland  (Fanfare LP N 46 146)
The Complete Blue Note Lee Morgan Fifties Sessions  (Mosaic MR6-162)
The Jazz Message Of Hank Mobley #2  (Savoy MG 12092)
Various Artists - Special College Jazz Album (complimentary record)  (Verve MGV 8341)
The Big Band Sound Of Dizzy Gillespie  (Verve (E) 2317 080)
Jimmy Smith - Special Guests  (Blue Note (J) BNJ-50101)
Art Blakey's Jazz Messengers - Des Femmes Disparaissent (Soundtrack)  (Fontana (F) 660 224 MR)
Piano Solo By Hank Jones - Urbanity  (Clef MGC 707)
Test1 - Test2 - Test3 (foo)  (None XYZ 1234)
"""

expected = [
    (None, 'Wardell Gray Memorial, Vol. 1', 'Prestige PRLP 7008'),
    ('Art Pepper With Sonny Clark Trio', 'Straight-Ahead Jazz, Vol. 1', 'Straight-Ahead Jazz SAJ-1001'),
    (None, 'The Sonny Clark Memorial Album', 'Xanadu 121'),
    ('Jimmy Raney/Sonny Clark', 'Together', 'Xanadu 209'),
    ("Howard Rumsey's Lighthouse All-Stars", 'Music For Lighthousekeeping', 'Contemporary C 3528'),
    ('Dizzy Gillespie', 'Big Band Live In Hi-Fi From Birdland', 'Fanfare LP N 46 146'),
    (None, 'The Complete Blue Note Lee Morgan Fifties Sessions', 'Mosaic MR6-162'),
    (None, 'The Jazz Message Of Hank Mobley #2', 'Savoy MG 12092'),
    ('Various Artists', 'Special College Jazz Album (complimentary record)', 'Verve MGV 8341'),
    (None, 'The Big Band Sound Of Dizzy Gillespie', 'Verve (E) 2317 080'),
    ('Jimmy Smith', 'Special Guests', 'Blue Note (J) BNJ-50101'),
    ("Art Blakey's Jazz Messengers", 'Des Femmes Disparaissent (Soundtrack)', 'Fontana (F) 660 224 MR'),
    ('Piano Solo By Hank Jones', 'Urbanity', 'Clef MGC 707'),
    ('Test1', 'Test2 - Test3 (foo)', 'None XYZ 1234')]

def test_titles():
    for line, e in zip(title_lines.strip().split("\n"), expected):
        artist, title, catalog_number = process_title(line)
        print(artist, title, catalog_number)
        assert (artist, title, catalog_number) == e

def test_nbsp_titles():
    line = 'Various Artists - The West Coast Jam Sessions \xa0(Jam Session No. 103)'
    artist, title, catalog_number = process_title(line)
    assert artist == 'Various Artists'
    assert title  == 'The West Coast Jam Sessions'
    assert catalog_number == 'Jam Session No. 103'

    line = 'Billy Eckstine - Mr. B \xa0(Ember (E) FA 2010)'
    artist, title, catalog_number = process_title(line)
    assert artist == 'Billy Eckstine'
    assert title  == 'Mr. B'
    assert catalog_number == 'Ember (E) FA 2010'

    line = 'Sonny Thompson - Jumping With The Rhumba / Gone Again Blues \xa0(King 4446)'
    artist, title, catalog_number = process_title(line)
    assert artist == 'Sonny Thompson'
    assert title  == 'Jumping With The Rhumba / Gone Again Blues'
    assert catalog_number == 'King 4446'

    line = 'Jaco Pastorius/Pat Metheny/Bruce Ditmas/Paul Bley \xa0(Improvising Artists Inc. IAI 37.38.46)'
    artist, title, catalog_number = process_title(line)
    assert artist == None
    assert title  == 'Jaco Pastorius/Pat Metheny/Bruce Ditmas/Paul Bley'
    assert catalog_number == 'Improvising Artists Inc. IAI 37.38.46'
