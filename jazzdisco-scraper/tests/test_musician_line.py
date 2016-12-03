from jazzdisco.utils import process_musician_line, musician_tuple


musicians = """\
<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Hank Jones</strong> [Henry Jones] (<em>b</em> Vicksburg, MS, July 31, 1918; <em>d</em> Manhattan, NY, May 16, 2010; aged 91) piano.</p>
<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Sonny Clark</strong> [Conrad Yeatis Clark] (<em>b</em> Herminie, nr Elizabeth, PA, July 21, 1931; <em>d</em> NYC, January 13, 1963; aged 31) piano.</p>
<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>McCoy Tyner</strong> [Alfred McCoy Tyner] (<em>b</em> Philadelphia, PA, December 11, 1938; age 77) piano.</p>
<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Miles Davis</strong> [Miles Dewey Davis III] (<em>b</em> Alton, IL, May 26, 1926; <em>d</em> Santa Monica, CA, September 28, 1991; aged 65) trumpet, leader.</p>
<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Sonny Rollins</strong> [Theodore Walter Rollins] (<em>b</em> NYC, September 7, 1930; age 86) tenor sax, soprano sax, Lyricon.</p>
"""

expected = [
('Hank Jones', 'Henry Jones', 'Vicksburg, MS', 'July 31, 1918', 'Manhattan, NY', 'May 16, 2010', ['piano']),
('Sonny Clark', 'Conrad Yeatis Clark', 'Herminie, nr Elizabeth, PA', 'July 21, 1931', 'NYC', 'January 13, 1963', ['piano']),
('McCoy Tyner', 'Alfred McCoy Tyner', 'Philadelphia, PA', 'December 11, 1938', None, None, ['piano']),
('Miles Davis', 'Miles Dewey Davis III', 'Alton, IL', 'May 26, 1926', 'Santa Monica, CA', 'September 28, 1991', ['trumpet', 'leader']),
('Sonny Rollins', 'Theodore Walter Rollins', 'NYC', 'September 7, 1930', None, None, ['tenor sax', 'soprano sax', 'Lyricon'])]


def test_musician_line():
    for line, e in zip(musicians.strip().split("\n"),expected):
        result = process_musician_line(line)
        print(result)
        assert result == musician_tuple(*e), result


def test_clifford_brown():
    line = '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Clifford Brown</strong> (<em>b</em> Wilmington, DE, October 30, 1930; <em>d</em> Bedford, PA, June 26, 1956; aged 25) trumpet.</p>'
    result = process_musician_line(line)
    assert result == musician_tuple('Clifford Brown', None, 'Wilmington, DE', 'October 30, 1930', 'Bedford, PA', 'June 26, 1956', ['trumpet'])


def test_incomplete_info():
    cases = [
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Steely Dan</strong> - Walter Becker/Donald Fagen\'s jazz rock band.</p>',
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Havana Jam</strong> - concerts.</p>',
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Petite Swanson</strong> [Alphonso Horsley] - female vocals.</p>',
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Willie Wilson</strong> (<em>b</em> 1930s; <em>d</em> 1963) trombone.</p>',
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Munyungo Jackson</strong> [Darryl J. Munyungo Jackson] (<em>b</em> Los Angeles, CA) percussion.</p>']

    expected = [
        ('Steely Dan', None, None, None, None, None, ['Walter Becker/Donald Fagen\'s jazz rock band']),
        ('Havana Jam', None, None, None, None, None, ['concerts']),
        ('Petite Swanson', 'Alphonso Horsley', None, None, None, None, ['female vocals']),
        ('Willie Wilson', None, None, None, None, None, ['trombone']),
        ('Munyungo Jackson', 'Darryl J. Munyungo Jackson', None, None, None, None, ['percussion'])]

    for line, e in zip(cases, expected):
        result = process_musician_line(line)
        assert result == musician_tuple(*e)


def test_variations():
    cases = [
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Tommy Turk</strong> (<em>b</em> Johnstown, PA, 1927; <em>d</em> 1981; aged 54/53) trombone.</p>',
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Joyce Collins</strong> (<em>b</em> Battle Mountain, NV, May 5, 1930; <em>d</em> January 3, 2010; aged 79) piano.</p>',
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Rocky Boyd</strong> [John Erskine Boyd] (<em>b</em> Boston, MA, 1936; age 80/79) tenor sax.</p>',
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Bill Leslie</strong> [William C. Leslie] (<em>b</em> Media, PA, 1925; <em>d</em> West Rockhill Township, Sellerville, PA, June 21, 2003; aged 78/77) tenor sax.</p>',
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Claude Williamson</strong> [Claude Berkeley Williamson] (<em>b</em> Brattleboro, VT, November 18, 1926; <em>d</em> July 16, 2016; aged 89) piano.</p>',
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Lucy Ann Polk</strong> (<em>b</em> Idaho, May 16, 1927; <em>d</em> October 10, 2011; aged 84) female vocals.</p>',
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Bjarne Rostvold (Danish)</strong> (<em>b</em> February 18, 1934; <em>d</em> July 12, 1989; aged 55) drums.</p>',
        '<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>Ronnie Ball (English)</strong> [Ronald Ball] (<em>b</em> Birmingham, England, December 22, 1927; <em>d</em> NYC, October, 1984; aged 56) piano.</p>']

    expected = [
        ('Tommy Turk', None, 'Johnstown, PA', '1927', None, '1981', ['trombone']),
        ('Joyce Collins', None, 'Battle Mountain, NV', 'May 5, 1930', None, 'January 3, 2010', ['piano']),
        ('Rocky Boyd', 'John Erskine Boyd', 'Boston, MA', '1936', None, None, ['tenor sax']),
        ('Bill Leslie', 'William C. Leslie', 'Media, PA', '1925', 'West Rockhill Township, Sellerville, PA', 'June 21, 2003', ['tenor sax']),
        ('Claude Williamson', 'Claude Berkeley Williamson', 'Brattleboro, VT', 'November 18, 1926', None, 'July 16, 2016', ['piano']),
        ('Lucy Ann Polk', None, 'Idaho', 'May 16, 1927', None, 'October 10, 2011', ['female vocals']),
        ('Bjarne Rostvold', None, None, 'February 18, 1934', None, 'July 12, 1989', ['drums']),
        ('Ronnie Ball', 'Ronald Ball', 'Birmingham, England', 'December 22, 1927', 'NYC', 'October, 1984', ['piano'])]

    for line, e in zip(cases, expected):
        result = process_musician_line(line)
        assert result == musician_tuple(*e), result


