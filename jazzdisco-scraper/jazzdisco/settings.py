# -*- coding: utf-8 -*-
# Scrapy settings for jazzdisco project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'jazzdiscospider'

SPIDER_MODULES = ['jazzdisco.spiders']
# NEWSPIDER_MODULE = 'jazzdisco.spiders'
# ITEM_PIPELINES = 

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'jazzdisco (+http://www.yourdomain.com)'

HTTPCACHE_ENABLED = True
HTTPCACHE_POLICY = "scrapy.extensions.httpcache.DummyPolicy"
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"
HTTPCACHE_DIR = "/Users/CBare/Documents/projects/jazz_discography/httpcache"


FEED_URI = "file:///Users/CBare/Documents/projects/jazz_discography/out.json"
FEED_FORMAT = "jsonlines"
FEED_EXPORT_ENCODING = "utf-8"

