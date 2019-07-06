
## Set up environment
. virtual-env-scrapy-py3/bin/activate
export PYTHONPATH=/Users/CBare/Documents/projects/jazz_discography/jazzdisco-scraper/:/Users/CBare/Documents/projects/jazz_discography/web


## Run scrapers
cd jazzdisco-scraper
scrapy crawl jazzdiscospider -o ../out.json
scrapy crawl labelspider -o ../data/label_data_jazzdisco.json
cd ..


## uniquify sessions
python scripts/unique_sessions.py

## Extract data to sqlite

sqlite3 data/jazz.sqlite
sqlite> .read scripts/drop_tables.sql
sqlite> .read scripts/create_tables.sql

$python python scripts/musicians_to_db.py
