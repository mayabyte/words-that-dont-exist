venv:
	virtualenv venv
	source venv/bin/activate
	pip3 install -r requirements.txt

entries.txt: venv
	python3 scraper.py

scrape: entries.txt

train: entries.txt
	python3 train.py

.PHONY: scrape, train