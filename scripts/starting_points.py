from utils import slugify

a = """\
Ron Carter
Miles Davis
Hank Jones
Clark Terry
Ray Brown
John Coltrane
Herbie Hancock
Kenny Burrell
Bill Evans
Chick Corea
Max Roach
Wayne Shorter
Elvin Jones
Art Blakey
Paul Chambers
Oscar Peterson
Eric Dolphy
Tommy Flanagan
Dizzy Gillespie
Chet Baker
Stan Getz
Sam Jones
Keith Jarrett
Milt Jackson
Charles Mingus
McCoy Tyner
Pat Metheny
Billy Higgins
Kenny Barron
Roy Haynes
Kenny Clarke
Percy Heath
Wynton Kelly
Oliver Nelson
John Lewis
Kenny Drew
Joe Henderson
Freddie Hubbard
Donald Byrd
Dexter Gordon
Dave Brubeck
Art Farmer
Bobby Hutcherson
Jimmy Cobb
Philly Joe Jones
Art Pepper
Joe Zawinul
Sonny Stitt
Lee Morgan
Johnny Griffin
Paul Desmond
Jim Hall
Charlie Parker
Gerry Mulligan
Johnny Hodges
Pepper Adams
Paul Motian
Ornette Coleman
J.J. Johnson
Cannonball Adderley
Sonny Rollins
Jimmy Garrison
Kenny Dorham
Blue Mitchell
Joe Pass
Thelonious Monk
Count Basie
Horace Silver
Ben Webster
Bud Powell
Lee Konitz
Hank Mobley
Duke Ellington
Hampton Hawes
Sonny Clark
Lester Young
"""


def by_last_name(name):
    fn,ln = name.rsplit(' ', 1)
    return ln, fn

names = sorted([name for name in a.strip().split('\n')], key=by_last_name)

for name in names:
    slug = slugify(name)
    print('    <li><a href="/{slug}">{name}</a></li>'.format(slug=slug, name=name))
