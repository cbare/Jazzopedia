virtualenv -p python3 virtual-env-scrapy-py3
. virtual-env-scrapy-py3/bin/activate
python --version
Python 3.5.1

pip install scrapy
pip install beautifulsoup4
pip install dateparser

export SCRAPY_SETTINGS_MODULE=settings.py



Album
-----
title
artist
year
catalog number
tracks[]

Track
-----
title
album
album artist
composer
grouping
genre
year
track n of m
comments

Session
-------


issues
------
same name (for example, Bill Evans)
identifying the same session on different pages



Jazzdisco.org
-------------
Session ids are given for each session, but they are not unique. They are essentially dates, in the form YYMMDD. Some are especially useless, for example 570000 meaning some unkown date in 1957.


