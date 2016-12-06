"""
Scrape label data from jazzdisco.org

A Scrapy scraper for the Jazz Discography Project (jazzdisco.org),
a jazz music resource by: Nobuaki Togashi, Kohji Matsubayashi, and
Masayuki Hatta.

$ scrapy labelspider
"""
import re, scrapy
import dateparser
import bs4
import jazzdisco
from io import StringIO
from jazzdisco.items import *
from jazzdisco.utils import *


lbl_re = re.compile(r'<p><img src="/images/right.gif" alt="" width="17" height="11"><strong>(.+)</strong> \(<em>e</em> (.+), (?:.+ )?(\d+); (.+)\) (.+).</p>')
alb_re = re.compile(r'(.*)   (?:(.+) - )?(.+)')


def parse_label_info(s):
    m = lbl_re.match(s)
    if m:
        name = m.group(1)
        established_place = m.group(2)
        established_year  = m.group(3)
        principals        = m.group(4)
        info              = m.group(5)
    else:
        raise RuntimeError("Can't parse: " + s)
    return( (name, established_place, established_year, principals, info) )


def parse_album_info(element):
    buffer = StringIO()
    for child in element.children:
        if type(child)==bs4.element.NavigableString:
            buffer.write(child)
    s = buffer.getvalue().strip()
    m = alb_re.match(s)
    if m:
        return (m.group(1), m.group(2), m.group(3))
    else:
        raise RuntimeError("Can't parse: " + s)


def get_catalog_entry(element):
    buffer = StringIO()
    while True:
        if type(element)==bs4.element.NavigableString:
            buffer.write(element)
        elif hasattr(element, 'name') and element.name in INLINE_ELEMENTS:
            buffer.write(''.join(element.strings))
        else:
            break
        element = element.nextSibling
    return buffer.getvalue().strip()


class LabelSpider(scrapy.Spider):
    """
    Scape whole site. Descend into release catalogs and session discography.
    """
    name = 'labelspider'
    start_urls = ['http://jazzdisco.org/']
    

    def __init__(self, *args, **kwargs):
        super(LabelSpider, self).__init__(*args, **kwargs)
        self.titles = set()
        self.processed_musicians = set()
        self.sessions = set()
        self.title_count = 0
        self.session_count = 0


    def closed(self, reason):
        print("\n\n")
        print("+~~~~~~~~~"*7)
        print("titles: ", len(self.titles), self.title_count)
        print("sessions: ", len(self.sessions), self.session_count)


    def parse(self, response):
        ## labels
        title = response.xpath("//div[@class='a-to-z-container']/div[@class='second-box']/h3[text()='List of Record Labels:']")
        names = title.xpath("following-sibling::ul[1]/li/a/text()").extract()
        links = title.xpath("following-sibling::ul[1]/li/a/@href").extract()
        for name, link in zip(names, links):
            yield scrapy.Request(response.urljoin(link), callback=self.parse_label)


    def parse_label(self, response):
        h = response.xpath("//h2[text()=\"Collector's Guides & Discographies\"]")
        line = h.xpath("following-sibling::p[1]").extract()[0]
        print(parse_label_info(line))

        ## get album catalog link
        links = response.xpath("//a[text()='Catalog']/@href").extract()
        for link in links:
            yield scrapy.Request(response.urljoin(link), callback=self.parse_catalog)

        ## get discography link
        links = response.xpath("//a[text()='Discography']/@href").extract()
        for link in links:
            print(link)
            yield scrapy.Request(response.urljoin(link), callback=self.parse_discography)


    def parse_catalog(self, response):
        soup = bs4.BeautifulSoup(response.body, 'lxml')

        h1 = soup.find(name='h1')
        if h1:
            catalog_label = h1.string

        catalog_data = soup.find(id='catalog-data')
        for album_header in catalog_data.find_all('h3'):
            anchor = album_header.find('a')
            catalog_slug = anchor['name']
            catalog_number, artist, title = parse_album_info(anchor)
            print("\n", "-"*60)
            print(catalog_number, artist, title)
            self.titles.add(title)
            self.title_count += 1

            m = re.match(r'(not used\??|no information)', title)
            if m:
                continue

            parts = []
            notes = None
            elem = consume_whitespace(album_header.next_sibling)
            if elem.name == 'h3' or elem.name == 'h2':
                pass
            elif elem.name == 'div' and elem.string == 'no details':
                pass
            else:
                while elem is not None:
                    personnel, elem = collect_text(elem)
                    personnel = clean_personnel(personnel)
                    print('personnel=', personnel)
                    if elem.name == 'div' and 'date' in elem['class']:
                        date,_ = collect_text(elem.next)
                    else:
                        date = None
                    print('date=', date)
                    elem = consume_whitespace(elem.next_sibling)
                    tracks = []
                    if elem.name == 'table':
                        for row in elem.find_all('tr'):
                            cells = row.find_all('td')
                            track_id = cells[0].string
                            track_name = cells[1].string
                            track_id = track_id.strip() if track_id else track_id
                            track_name = track_name.strip() if track_name else track_name
                            tracks.append(Track(id=track_id, name=track_name))
                    else:
                        raise RuntimeError("Expected a table of tracks")
                    elem = elem.next_sibling
                    print('tracks=', tracks)
                    parts.append(Part(personnel=personnel, date=date, tracks=tracks))

                    notes, look_ahead = collect_text(elem)
                    if look_ahead is None or look_ahead.name in ['h3','h2']:
                        break

            yield Release(title=title, artist=artist, catalog_source=catalog_label, source_url=response.url, catalog_slug=catalog_slug, catalog_number=catalog_number, notes=notes, parts=parts)


    def parse_discography(self, response):
        soup = bs4.BeautifulSoup(response.body, 'lxml')

        h1 = soup.find(name='h1')
        if h1:
            catalog_label = h1.string
        print(catalog_label)

        catalog_data = soup.find(id='discography-data')
        for album_header in catalog_data.find_all('h3'):
            print(album_header.string)

            anchor = album_header.find('a')
            session_id = anchor['name']
            title = anchor.string
            self.sessions.add(title)
            self.session_count += 1
            parts = []

            ## for each part
            elem = album_header.next_sibling
            while elem is not None:
                personnel, elem = collect_text(elem)
                personnel = clean_personnel(personnel)
                if elem.name == 'div' and 'date' in elem['class']:
                    date,_ = collect_text(elem.next)
                else:
                    raise RuntimeError('Missing date for title: %s'%title)
                tracks = []
                elem = consume_whitespace(elem.next_sibling)
                if elem.name == 'table':
                    for row in elem.find_all('tr'):
                        cells = row.find_all('td')
                        track_id = cells[0].string
                        track_name = cells[1].string
                        catalog_id = cells[2].string
                        track_id = track_id.strip() if track_id else track_id
                        track_name = track_name.strip() if track_name else track_name
                        catalog_id = catalog_id.strip() if catalog_id else catalog_id
                        tracks.append(Track(id=track_id, name=track_name, issued=catalog_id))
                    parts.append(Part(personnel=personnel, date=date, tracks=tracks))
                    elem = elem.next_sibling
                else:
                    raise RuntimeError("Expected a table of tracks")

                ## After one or more parts comes some notes, but we don't
                ## know if we're at the end until we find an h2 or h3 after
                ## the text block.
                notes, look_ahead = collect_text(elem)
                if look_ahead is None or look_ahead.name in ['h3','h2']:
                    break

            yield Session(group=title, session_id=session_id, catalog_source=catalog_label, source_url=response.url+'#'+session_id, notes=notes, parts=parts)



