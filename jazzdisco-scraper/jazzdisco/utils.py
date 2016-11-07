# -*- coding: utf-8 -*-
"""
Helper functions for parsing parts of jazzdisco.org
"""
import bs4
import re


def consume_whitespace(elem):
    """
    Advance to the next DOM sibling element that is not whitespace
    """
    while type(elem)==bs4.element.NavigableString and elem.string.strip() == '':
        elem = elem.next_sibling
    return child


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
        name = m.group(1)
        full_name = m.group(2)
        roles = m.group(4)
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
    m = re.match(r'(?:(.+?) - )?(.*)\s\s\((.+)\)$', line.strip())
    if m:
        return m.group(1), m.group(2), m.group(3)
    else:
        raise RuntimeError("Unable to parse title line.", line)


def process_personnel(line):
    """
    Split personnel line into pairs of name, intrument
    """
    match_iter = re.finditer(r'\s*(?:([^()]+?) \(([^()]+?)\))', line)
    for m in match_iter:
        names = re.split(",\s*", m.group(1))
        instruments = re.split(",\s+", m.group(2))
        for name in names:
            for instrument in instruments:
                yield name, instrument


def clean_personnel(line):
    m = re.match(r'\s*<span class="same">(.+?):\s</span>same\s(?:personnel|session)\s*', line)
    if m:
        return m.group(1)
    else:
        return line

