# -*- coding: utf-8 -*-
import scrapy

class Musician(scrapy.Item):
    name = scrapy.Field()
    full_name = scrapy.Field()
    birth_date = scrapy.Field()
    birth_place = scrapy.Field()
    death_date = scrapy.Field()
    death_place = scrapy.Field()
    roles = scrapy.Field()

class Track(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    issued = scrapy.Field()

class Part(scrapy.Item):
    personnel = scrapy.Field()
    date = scrapy.Field()
    tracks = scrapy.Field()

class Release(scrapy.Item):
    title = scrapy.Field()
    catalog_slug = scrapy.Field()
    catalog_number = scrapy.Field()
    year = scrapy.Field()
    notes = scrapy.Field()
    parts = scrapy.Field()

class Session(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    year = scrapy.Field()
    notes = scrapy.Field()
    parts = scrapy.Field()
