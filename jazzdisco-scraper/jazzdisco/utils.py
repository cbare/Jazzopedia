# -*- coding: utf-8 -*-
"""
Helper functions for parsing parts of jazzdisco.org
"""
import bs4
import re

alternate_names = {}
with open('/Users/CBare/Documents/projects/jazz_discography/data/alternate_names.txt') as f:
    for line in f:
        names = line.strip().split('|')
        for name in names:
            alternate_names[name] = names[0]


def consume_whitespace(elem):
    """
    Advance to the next DOM sibling element that is not whitespace
    """
    while type(elem)==bs4.element.NavigableString and elem.string.strip() == '':
        elem = elem.next_sibling
    return elem


def collect_text(elem):
    """
    Collect the contents for a series of text DOM elements
    """
    results = ""
    while elem is not None and \
        (    type(elem)==bs4.element.NavigableString \
          or type(elem)==bs4.element.Comment \
          or elem.name in ['b', 'i', 'em', 'strong', 'u', 'br']\
          or (elem.name=='span' and 'same' in elem.get('class', []))):
        if type(elem)==bs4.element.Comment:
            pass
        else:
            results += str(elem)
        elem = elem.next_sibling
    return results.strip(), elem


def process_musician_line(line):
    """
    Split musician line into name, full name, birth place, birth date, died place
    died date, and roles (intruments, etc.)
    """

    # (?:\s*\[(.*?)\])?\s+\(<em>b</em>\s*(.+?),\s*(?:January|February|March|April|May|June|July|August|September|October|November|December) \d+, \d+;)\s*(?:<em>d</em> (.+?),\s*((?:January|February|March|April|May|June|July|August|September|October|November|December) \d+, \d+);)?\s*aged? \d+ 
    musician_line_template = r'<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>(.+?)</strong>\s+(?:\[(.*?)\]\s+)?(?:(?:\((.*?)\))|-)\s+(.+?).</p>'
    place_date_template = r'<em>%s</em>\s*(?:([^;]+?),\s*)?((?:January|February|March|April|May|June|July|August|September|October|November|December)(?: \d+)?, \d{4});'
    place_year_template = r'<em>%s</em>\s*(?:([^;]+?),\s*)?(\d{4});'

    m = re.match(musician_line_template, line)
    if m:
        ## remove national origin suffixes, for example "Oscar Peterson (Canadian)"
        ## or "Wynton Kelly (Jamaican-American)"
        name = re.sub(r'\s+\(.+\)$', '', m.group(1))
        full_name = m.group(2)
        roles = re.split(',\s*', m.group(4))
        birth_and_death = m.group(3)

        birth_place = birth_date = death_place = death_date = None

        if birth_and_death:
            b = re.search(place_date_template%'b', birth_and_death)
            if not b:
                b = re.search(place_year_template%'b', birth_and_death)
            if b:
                birth_place = b.group(1)
                birth_date = b.group(2)

            d = re.search(place_date_template%'d', birth_and_death)
            if not d:
                d = re.search(place_year_template%'d', birth_and_death)
            if d:
                death_place = d.group(1)
                death_date = d.group(2)

        return musician_tuple(name, full_name, birth_place, birth_date, death_place, death_date, roles)
    else:
        raise RuntimeError("Unable to parse musician info line.", line)


def musician_tuple(*args):
    return list(zip(('name', 'full_name', 'birth_place', 'birth_date', 'death_place', 'death_date', 'roles'), args))


def process_title(line):
    """
    Split title line into artist, title, and catalog number
    """
    m = re.match(r'(.*?)\s\s\((.+)\)$', line.strip())
    if m:
        artist = None
        title = m.group(1)
        catalog_number = m.group(2)

        fields = re.split(r' - ', title)
        if len(fields) == 2:
            artist = fields[0]
            title  = fields[1]

        return artist, title, catalog_number
    else:
        raise RuntimeError("Unable to parse title line.", line)

def is_personnel_junk(name):
    junk = ['others?', 'organ', 'harp', 'woodwinds and strings', 'vocal group',
            'the orchestra features many UCLA jazz program students',
            'the strings of The London Symphony Orchestra', 'guitar',
            'overdubbed 14 piece strings', 'two others', 'choir', 'replaces unknown',
            'strings quartet', 'assisted by Amiya Das Gupta', 'all these and others',
            'reeds and rhythm','horns/reeds: Marvin Stamm', 'various unknown', 'trombone',
            'traditional Ladino poem', 'female voice', 'traditional', 'four trombones section',
            'two unknown', 'flutes', 'everybody', 'radio.string.quartet.vienna: Igmar Jenner',
            'choirs', 'horns and strings', 'congregation', 'mixed vocal choir',
            'brass organ and rhythm', 'directed by Elizabeth Min', 'on Rudy Bird',
            'harp and strings', 'drums', 'clarinets', 'replaces African percussion ensemble',
            'others', 'saxes', 'maybe Cornell Dupree', 'piano', 'female voices', 'rhythm',
            'strings and French horns', 'strings and female voices', 'percussion', 'strings and choir',
            'assisted by Shyam But-Nagar', 'four others', 'nine strings section', 'alto sax',
            'electric bass', 'add The Merry Young Souls', 'various friends', 'strings',
            'others unknown but possibly include Barney Bigard', 'strings and female vocals group',
            'four 39-piece orchestras From The Oberlin College Conservatory Of Music',
            'strings and chorus', 'vibes', 'rhythm and strings', 'reeds and vocals',
            'reeds and strings', 'reeds', 'percussion and choir', 'piano/organ',
            'one unknown', 'unknown', 'Unknown Philipino', '9th Wonder', 'Wendy',
            'a french horn', 'a harp', 'Al', 'Alabama Sacred Harp Singers',
            'AMOA', 'Amsterdam Sinfonietta', 'anonymous', 'another female?',
            'bass', 'ABC Messenger delivery man', 'African percussion ensemble',
            'Afrikan Bag Productions', 'woodwinds', 'Welfare City Choir', 'Welfo',
            'We Wear The Crown', 'WDR Sinfonieorchester Koln',
            'Radio Symphonieorchester Wien', 'Radio-Symphonieorchester Wien',
            'M\'Boom Re:percussion Ensemble', 'Johnson', '.. Johnson',
            'George Duvivier or Al Lucas or Art Davis', 'RM', 'Ed', 'Ou ......',
            'Gu ......', 'Han ......', 'Inc.', 'Don', 'Ed', 'Hart', 'KING', 'Brown', 'Big Chief',
            'White', 'Sha', '"Chan"', 'Jones', 'Carl', 'Valent', 'Mina', 'Nya', 'Theo',
            'Thelma', 'Sylvester', 'SWR Stuttgart Radio Symphony Orchestra', 'Stuttgart',
            'SWR Vokalensemble Stuttgart', 'Stuttgarter Kammerorchester',
            'Swedish Radio Symphony Orchestra', 'Swedish Radio Choir', 'Branch', 'George',
            'Jack', 'Jackson', 'Stephanie', 'St Luke', 'Choir', 'Jimmy', 'Spanky', 'S S',
            '"Sidney"', 'Harold', 'Sarah', 'Rhodes', 'Sabu', 'Buffin', 'Sims', '"Marie"',
            'Max', 'Albert', 'Heath', 'Keith', 'Julia', 'Pete', 'Wolfert Brederode Quartet',
            'D.ST.', 'Billy', 'Charlie', 'Duke Ellington School Of Arts Show Choir',
            'Ensemble Modern Orchestra', 'Ensemble Modern', 'Marcus', 'Machito And His Orhestra',
            'Sermons With Congregation Of New Bethel Baptist Church', 'Congregation',
            'Shedryk Children\'s Choir', 'Children\'s Choir', 'Scott',
            'Toshiyuki Miyama And His New Herd Orchestra', 'Texas Top Hands', 'Top Hands',
            'Patti LaBelle And The Bluebelles', 'Oliver Nelson Orchestra',
            'Norwegian Radio Orchestra', 'Norwegian', 'New Japan Philharmonic Orchestra',
            'New Japan Philharmonic', 'New York Group Singer\'s Big Band', 'GROUP',
            "'Memphis'", 'Tommy Brown Gospel Singer', 'Nobuo Hara Sharps And Flats',
            'Lenny Druss horns and Sol Bobrov strings', 'Frank Humphries And His Orchestra',
            'Eddie Williams And The Crusaders', 'Barbara', 'Barney Kessel Orchestra']

    if name in junk:
        return True

    if re.match(r'^\d+\s+(strings|violins)', name):
        return True

    if name.startswith('The ') or name.startswith('or '):
        return True

    if name.startswith('vocal') or name.startswith('voices:'):
        return True

    if name.startswith('??? ') or name.endswith('???'):
        return True

    if name.startswith('AfroCuba De Matanzas:'):
        return True

    if name.startswith('American Composer') or name.startswith('woodwind quartet: '):
        return True

    if name.startswith('unknown') or name.startswith('unidentified'):
        return True

    return False


def remove_track_references(s):
    return re.sub(r'\s+-\d+([/,]\d+)*$', '', s)

def process_personnel(line):
    """
    Split personnel line into pairs of name, intrument
    """
    line = re.sub(r'<span class="same">', '', line)
    line = re.sub(r'</span>', '', line)
    line = re.sub(r'plus overdubs: ', '', line)
    line = re.sub(r'plus an overdub: ', '', line)
    line = re.sub(r'special thanks( to)?:? ', '', line)
    line = re.sub(r'frontground vocals: ', '', line)
    line = re.sub(r'percussions?: ', '', line)
    line = re.sub(r'guest (appearances|musicans|vocalists|vocals): ', '', line)
    line = re.sub(r' and his string section', '', line)
    line = re.sub(r'  And The Philadelphia Strings And Horns', '', line)
    match_iter = re.finditer(r'\s*(?:([^()]+?) \(([^()]+?)\))', line)
    for m in match_iter:
        names = re.split(",\s*", m.group(1))
        instruments = re.split(",\s+", m.group(2))
        for name in names:
            if re.match('^\d+[ -?]', name):
                continue
            name = re.sub(r'^[:.]\s*', '', name)
            name = re.sub(r'^with the orchestra: violins: ', '', name)
            name = re.sub(r'^accompanied by Eddie Safranski And His Orchestra: ', '', name)
            name = re.sub(r'^(added|including|(and )?introducing|add( plus)?|with|With|plus|and|on|duet( with)?|accompanied by|poss\.|\+):?\s+', '', name)
            name = re.sub(r'^quartet \d+: ', '', name)
            name = re.sub(r'^sequence \d+(/\d+)*: ', '', name)

            # name = re.sub(r'special guest star:\s*', '', name)
            # name = re.sub(r'overdubs:\s*', '', name)
            # name = re.sub(r'background vocals?: ', '', name)
            # name = re.sub(r'(a full )?orchestra:\s*', '', name)
            # name = re.sub(r'(with )?(special )?guests?( (artist|musician))?s?: ', '', name)
            name = re.sub(r'^featuring:? ', '', name)
            name = re.sub(r'^alto/bass flutes: ', '', name)
            name = re.sub(r'^(special )?thanks( to)?(/featuring)?:\s*', '', name)
            # name = re.sub(r'additional [\w\s]+: ', '', name)
            # name = re.sub(r'also featuring: ', '', name)
            # name = re.sub(r'Arditti (String )?Quartet: ', '', name)
            # name = re.sub(r'Auryn Quartett: ', '', name)
            # name = re.sub(r'(basses|violins|violas): ', '', name)
            # name = re.sub(r'(Bergen Big Band|Zehetmair Quartett): ', '', name)
            # name = re.sub(r'ASCH Trio: ', '', name)
            # name = re.sub(r'AEquatuor: ', '', name)
            name = re.sub(r'^[\w\'\.\-"]+( [\w\'\.\-"]+)*: ', '', name)
            name = re.sub(r'Basie plays', 'Count Basie', name)
            name = re.sub(r' plays$', '', name)
            name = re.sub(r' Trio$', '', name)
            name = re.sub(r' Quartet$', '', name)
            name = re.sub(r'x Carla Bley', 'Carla Bley', name)
            name = re.sub(r'yasiin bey', 'Yasiin Bey', name)
            name = re.sub(r'w/ The M6: Sasha Bogdanowitsch', 'Sasha Bogdanowitsch', name)
            name = re.sub(r'string Gene Orloff', 'Gene Orloff', name)
            name = re.sub(r'additional Michael Fenelly', 'Michael Fenelly', name)
            name = re.sub(r' as .*', '', name)
            if is_personnel_junk(name):
                continue
            if name in alternate_names:
                name = alternate_names[name]
            for instrument in instruments:
                yield name, remove_track_references(instrument)


def clean_personnel(line):
    m = re.match(r'\s*<span class="same">(.+?):\s</span>same\s(?:personnel|session)\s*', line)
    if m:
        return m.group(1)
    else:
        return line

