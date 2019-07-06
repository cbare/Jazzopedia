"""
Figure out how to parse record labels and their kooky catalog numbers
"""

examples = """\
** also issued on Savoy SST 13008.
** also issued on Impulse! AS-9125.
** also issued on Prestige PR 7748 entitled "Cry-Tender!". Original Jazz Classics OJC-482, OJCCD-482-2.
** also issued on Riverside RLP 1176; Original Jazz Classics OJCCD-759-2. Riverside RS 3011 entitled "This Is Yusef Lateef".
** also issued on Riverside RS 9337; Original Jazz Classics OJCCD-721-2.
** also issued on New Jazz NJLP 8261; Prestige PR 7398; Original Jazz Classics OJCCD-917-2.
** also issued on Fantasy LP 3332, LP 8074 entitled "Dave Brubeck/Cal Tjader - Brubeck-Tjader". America (F) 30 AM 6095.
** also issued on Fantasy LP 8092. America (F) 30 AM 6068 entitled "The Genius Of Dave Brubeck".
** also issued on Sandy Hook SH 2064 entitled "Rare Radio Recordings 1953, 1954".
** also issued on Philology (It) W 51.2.
** also issued on Blue Vox (Swi) B/90174 entitled "Dave Brubeck Feat. Paul Desmond - Live Together".
** also issued on Columbia CS 8156; CBS (E) BPG 62065.
** also issued on Fontana (E) STFL 591, (Eu) 680 971 TL; Epic LA 16032, BA 17032.
** also issued on Columbia CS 9075; Columbia/Legacy CK 46189.
"""

expected = [
    [('Savoy','SST 13008')],
    [('Impulse!','AS-9125')],
    [('Prestige ','PR 7748'),
     ('Original Jazz Classics','OJC-482'),
     ('Original Jazz Classics','OJCCD-482-2')],
    [('Riverside','RLP 1176'),
     ('Original Jazz Classics','OJCCD-759-2'),('Riverside','RS 3011')],
    [('Riverside','RS 9337'),
     ('Original Jazz Classics','OJCCD-721-2')],
    [('New Jazz','NJLP 8261'),
     ('Prestige','PR 7398'),
     ('Original Jazz Classics','OJCCD-917-2')],
    [('Fantasy','LP 3332'),
     ('Fantasy','LP 8074'),
     ('America','30 AM 6095')],
    [('Fantasy','LP 8092'),
     ('America','30 AM 6068')],
    [('Sandy Hook','SH 2064')],
    [('Philology', 'W 51.2')],
    [('Blue Vox','B/90174')],
    [('Columbia','CS 8156'),('CBS','BPG 62065')],
    [('Fontana','STFL 591'),('Fontana','680 971 TL'),('Epic','LA 16032'),('Epic','BA 17032')],
    [('Columbia','CS 9075'), ('Columbia/Legacy','CK 46189')]]


def parse_album_catalog_numbers(line):
    """
    ** also issued on {label} {country} {cat#}, {country} {cat#}; {label} {cat#} entitled "This Is Yusef Lateef".
    """
    regex = r'^\*\* also issued on ([A-Z].+?) (\(\w+?\))? [A-Z0-9]+(?:[ -.][A-Z0-9]+)*.$'


regex = r'^\*\* also issued on ([A-Z].+?)(?: (\(\w+?\)))? ([A-Z0-9]+(?:[ -.][A-Z0-9]+)*).$'
m = re.match(regex, '** also issued on Dammit XYZ-1234-222.')
print(m.groups())
m = re.match(regex, '** also issued on Dammit (It) AB 1234.')
print(m.groups())


