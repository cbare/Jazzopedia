from jazzdisco.utils import process_personnel, clean_personnel


personnel_lines = """\
Charles Lloyd (tenor sax, flute) Keith Jarrett (piano) Cecil McBee (bass) Jack DeJohnette (drums): 
Charles Lloyd (tenor sax, flute) Keith Jarrett (piano, soprano sax) Ron McClure (bass) Jack DeJohnette (drums)
Keith Jarrett (piano, soprano sax, recorder) Charlie Haden (bass) Paul Motian (drums): 
Gary Burton (vibes) Keith Jarrett (piano, electric piano, soprano sax) Sam Brown (guitar) Steve Swallow (bass) Bill Goodwin (drums)
Keith Jarrett (piano) Richard Tee (organ) Bill Salter (bass) Grady Tate (drums) Ralph MacDonald (percussion, congas) Barbara Massey (vocals, piano, electric piano, autoharp) Ernie Calabria (vocals, guitar, 12-string guitar, electric sitar, arranger) Myrna Summers And The Interdenominational Singers, Eumir Deodato (conductor)
Bob Crull, Don Jacoby, Gary Slavo, Tom Wirtel, Chris Witherspoon (trumpet) Dee Barton, Willie Barton, Loren William Binford, Dave Wheeler (trombone) Al Beuler, John Giordano (alto sax) Don Melka, Bob Pierson (tenor sax) Jerry Keys (baritone, alto sax) Keith Jarrett (piano) Don Gililland (guitar) Toby Guynn (bass) John Van Ohlen (drums)
Miles Davis (trumpet) Steve Grossman (soprano sax) Keith Jarrett (organ) Chick Corea, Herbie Hancock (electric piano) Ron Carter (bass) Jack DeJohnette (drums) Airto Moreira (percussion) Hermeto Pascoal (voice, drums)
Keith Jarrett (piano) Paul Griffin (organ) Jerry Jemmott (electric bass) Bernard Purdie (drums) Marion Williams (vocals) The Dixie Hummingbirds: Ira Tucker, Willie Bobo, Beachey Thompson, James Davis, James Walker, Howard Carroll (backing vocal group) John Murtaugh (director)
Keith Jarrett (piano) Richie Resnicoff (guitar) Bill Salter (bass) Grady Tate (drums) Donal Leace (vocals, guitar) plus overdubs: unidentified horns and strings, Eumir Deodato (arranger)
Keith Jarrett (piano) David Spinozza (guitar) Bill Salter (bass) Bill LaVorgna (drums) Donal Leace (vocals, guitar) Roberta Flack (backing vocals -1) plus overdubs: unidentified horns and strings, Eumir Deodato (arranger)
Dewey Redman (tenor sax -1/4,6/9) Keith Jarrett (piano, soprano sax, steel drums, congas -1/4,6/9, piano -5) Charlie Haden (bass, steel drums -1/4,6/9) Paul Motian (drums, steel drums, congas -1/4,6/9)
Burt Collins, Mel Davis, Alan Rubin (trumpet, flugelhorn) Wayne Andre, Garnett Brown, Joe Wallace (trombone) Hubert Laws (flute) Airto (wood flute, percussion) Joe Farrell (soprano sax, alto, bass flute, piccolo) Keith Jarrett (piano) Jay Berliner (guitar) Ron Carter (bass) Don Sebesky (arranger)
"""

def test_personnel():
    results = []
    for line in personnel_lines.strip().split("\n"):
        for name, instr in process_personnel(line):
            print(name, instr)
            results.append((name, instr))

    assert ('Ernie Calabria', 'vocals') in results
    assert ('Ernie Calabria', 'guitar') in results
    assert ('Ernie Calabria', '12-string guitar') in results
    assert ('Ernie Calabria', 'electric sitar') in results
    assert ('Ernie Calabria', 'arranger') in results
    assert ('Eumir Deodato', 'conductor') in results
    assert ('Bob Crull', 'trumpet') in results
    assert ('Don Jacoby', 'trumpet') in results
    assert ('Gary Slavo', 'trumpet') in results
    assert ('Tom Wirtel', 'trumpet') in results
    assert ('Chris Witherspoon', 'trumpet') in results
    assert ('Dewey Redman', 'tenor sax -1/4,6/9') in results
    assert ('Charlie Haden', 'steel drums -1/4,6/9') in results
    assert ('Paul Motian', 'congas -1/4,6/9') in results
    assert ('Burt Collins', 'trumpet') in results
    assert ('Burt Collins', 'flugelhorn') in results
    assert ('Mel Davis', 'trumpet') in results
    assert ('Mel Davis', 'flugelhorn') in results
    assert ('Alan Rubin', 'trumpet') in results
    assert ('Alan Rubin', 'flugelhorn') in results
    assert ('Joe Farrell', 'piccolo') in results

def test_same_personnel():
    example = "<span class=\"same\">Duke Pearson (piano) Gene Taylor (bass) Lex Humphries (drums): </span>same personnel"
    assert clean_personnel(example) == "Duke Pearson (piano) Gene Taylor (bass) Lex Humphries (drums)"

    example = '<span class="same">Gail Brockman, Dizzy Gillespie, Marion Hazel, Shorty McConnell (trumpet) Joe Taswell Baird, Chippy Outcalt, Howard Scott (trombone) Gerald "Gerry" Valentine (trombone, arranger) Bill Frazier, John Jackson (alto sax) Gene Ammons, Dexter Gordon (tenor sax) Leo Parker (baritone sax) John Malachi (piano, arranger) Connie Wainwright (guitar) Tommy Potter (bass) Art Blakey (drums) Sarah Vaughan (vocals) Billy Eckstine (vocals, valve trombone, conductor) Tadd Dameron (arranger): </span>same session'
    assert clean_personnel(example) == "Gail Brockman, Dizzy Gillespie, Marion Hazel, Shorty McConnell (trumpet) Joe Taswell Baird, Chippy Outcalt, Howard Scott (trombone) Gerald \"Gerry\" Valentine (trombone, arranger) Bill Frazier, John Jackson (alto sax) Gene Ammons, Dexter Gordon (tenor sax) Leo Parker (baritone sax) John Malachi (piano, arranger) Connie Wainwright (guitar) Tommy Potter (bass) Art Blakey (drums) Sarah Vaughan (vocals) Billy Eckstine (vocals, valve trombone, conductor) Tadd Dameron (arranger)"

    example = '<span class="same">Eric Dolphy (alto sax, flute) Nathan Gershman (cello) John Pisano (guitar) Hal Gaylor (bass) Chico Hamilton (drums): </span>same session'
    assert clean_personnel(example) == "Eric Dolphy (alto sax, flute) Nathan Gershman (cello) John Pisano (guitar) Hal Gaylor (bass) Chico Hamilton (drums)"


