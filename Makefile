venv:
	virtualenv venv
	source venv/bin/activate
	pip3 install -r requirements.txt

entries.txt: venv
	python3 scraper.py

scrape: entries.txt

.PHONY: scrape