"""
Scrape data from jazzdisco.org

A Scrapy scraper for the Jazz Discography Project (jazzdisco.org),
a jazz music resource by: Nobuaki Togashi, Kohji Matsubayashi, and
Masayuki Hatta.
"""
import re, scrapy
import dateparser
import bs4
import jazzdisco
from jazzdisco.items import *
from jazzdisco.utils import *


class JazzDiscoSpider(scrapy.Spider):
    """
    Scape whole site. Descend into release catalogs and session discography.
    """
    name = 'jazzdiscospider'
    start_urls = ['http://jazzdisco.org/']
    

    def __init__(self, *args, **kwargs):
        super(JazzDiscoSpider, self).__init__(*args, **kwargs)
        self.titles = set()
        self.processed_musicians = set()
        self.sessions = set()
        self.title_count = 0
        self.session_count = 0


    def closed(self, reason):
        print("\n\n")
        print("+~~~~~~~~~"*7)
        print("musicians: ", len(self.processed_musicians))
        print("titles: ", len(self.titles), self.title_count)
        print("sessions: ", len(self.sessions), self.session_count)


    def parse(self, response):

        ## first column of musicians
        title = response.xpath("//div[@class='a-to-z-container']/div[@class='first-box']/h3")
        names = title.xpath("following-sibling::ul[1]/li/a/text()").extract()
        links = title.xpath("following-sibling::ul[1]/li/a/@href").extract()
        for name, link in zip(names, links):
            yield scrapy.Request(response.urljoin(link), callback=self.parse_musician)

        ## second column of musicians
        box = response.xpath("//div[@class='a-to-z-container']/div[@class='second-box']")
        names = box.xpath("ul[1]/li/a/text()").extract()
        links = box.xpath("ul[1]/li/a/@href").extract()
        for name, link in zip(names, links):
            yield scrapy.Request(response.urljoin(link), callback=self.parse_musician)

        ## labels
        # names = box.xpath("ul[2]/li/a/text()").extract()
        # links = box.xpath("ul[2]/li/a/@href").extract()
        # for name, link in zip(names, links):
        #     print("\n", "-----"*12)
        #     print(name)


    def parse_musician(self, response):
        h = response.xpath("//h2[text()=\"Collector's Guides & Discographies\"]")
        line = h.xpath("following-sibling::p[1]").extract()[0]
        fields = process_musician_line(line)

        ## get album catalog link
        catalog_link = response.xpath("//a[text()='Catalog']/@href").extract()
        yield scrapy.Request(response.urljoin(catalog_link[0]), callback=self.parse_catalog)

        ## get Discography link to sessions
        sessions_link = response.xpath("//a[text()='Discography']/@href").extract()
        yield scrapy.Request(response.urljoin(sessions_link[0]), callback=self.parse_sessions)

        ## add to set of processed musicians
        url = response.xpath("/html/head/base/@href").extract()[0]
        ## for example: 'http://www.jazzdisco.org/sonny-clark/'
        slug = url[25:-1]
        self.processed_musicians.add(slug)
        yield Musician(fields+[('slug',slug)])

        ## queue up related musicians
        container = response.xpath("//div[@id='sidebar']/div[@id='sidebar-see-also']/div[@class='a-to-z-container']")
        related_links = container.xpath("div[@class='first-box']/ul/li/a/@href").extract() + \
                        container.xpath("div[@class='second-box']/ul/li/a/@href").extract() + \
                        container.xpath("div[@class='last-box']/ul/li/a/@href").extract()
        for link in related_links:
            yield scrapy.Request(response.urljoin(link), callback=self.parse_musician)


    def parse_catalog(self, response):
        soup = bs4.BeautifulSoup(response.body, 'lxml')

        h1 = soup.find(name='h1')
        if h1:
            catalog_artist = ''.join(h1.strings).replace(' Catalog', '')

        catalog_data = soup.find(id='catalog-data')
        for year_header in catalog_data.find_all('h2'):
            year = re.sub(r'\(aged?\s+\d+\)', '', year_header.string)

            for sibling in year_header.find_all_next():
                if sibling.name == 'h2':
                    break
                elif sibling.name == 'h3':
                    anchor = sibling.find('a')
                    catalog_slug = anchor['name']
                    artist, title, catalog_number = process_title(anchor.string)
                    self.titles.add(title)
                    self.title_count += 1
                    parts = []

                    ## for each part
                    elem = sibling.next_sibling
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
                                track_id = track_id.strip() if track_id else track_id
                                track_name = track_name.strip() if track_name else track_name
                                tracks.append(Track(id=track_id, name=track_name))
                            parts.append(Part(personnel=personnel, date=date, tracks=tracks))
                            elem = elem.next_sibling
                        else:
                            raise RuntimeError("Expected a table of tracks")

                        notes, look_ahead = collect_text(elem)
                        if look_ahead is None or look_ahead.name in ['h3','h2']:
                            break

                    yield Release(title=title, artist=artist, catalog_source=catalog_artist, catalog_slug=catalog_slug, catalog_number=catalog_number, year=year, notes=notes, parts=parts)


    def parse_sessions(self, response):
        soup = bs4.BeautifulSoup(response.body, 'lxml')

        h1 = soup.find(name='h1')
        if h1:
            artist = ''.join(h1.strings).replace(' Discography', '')

        catalog_data = soup.find(id='discography-data')
        for year_header in catalog_data.find_all('h2'):
            year = re.sub(r'\(aged?\s+\d+\)', '', year_header.string)

            for sibling in year_header.find_all_next():
                if sibling.name == 'h2':
                    break
                elif sibling.name == 'h3':
                    anchor = sibling.find('a')
                    session_id = anchor['name']
                    title = anchor.string
                    self.sessions.add(title)
                    self.session_count += 1
                    parts = []

                    ## for each part
                    elem = sibling.next_sibling
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

                    yield Session(group=title, session_id=session_id, catalog_source=artist, year=year, notes=notes, parts=parts)



