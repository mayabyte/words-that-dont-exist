# words that don't exist

A dumb little robot that writes nonsensical dictionary entries for fake words.
<hr />

## Setup

Make a virtual environment for Python. Please.
```bash
virtualenv venv
source venv/bin/activate
```

Install the dependencies:
```bash
pip3 install -r requirements.txt
```

You also need to install Tensorflow - which type you want/can use is up to you. Note that you can't use Tensorflow 2.0+ because GPT2 depends on the `contrib` package, so pick a 1.X version you like. You probably want *one of* the following depending on your hardware:
```bash
pip3 install tensorflow==1.15.2
pip3 install tensorflow-gpu==1.15.2
```

## Usage
There are two (soon to be more) components to this project:
1. Scraper for words and their corresponding dictionary entries
1. GPT2 wrapper that trains a model and generates fake dictionary entries

### Running the scraper
Just set it loose with
```bash
python3 scraper.py
```
This will download a list of words into `words.txt` and try to fetch a dictionary entry from Merriam-Webster for each one. It is *lossy*, so you're not going to get a well-formed entry for every word in the list, and non-well-formed ones are discarded. It is also *slow* and will depend heavily on your internet connection speed, whether or not you're using a proxy or a VPN, etc.

The scraper works in batches: after each batch, all the words it's managed to scrape are appended to the `entries.txt` file. This means you can interrupt scraping at any time and everything up to the completion of the last chunk will be saved. Upon restarting the scraper, `entries.txt` is scanned for words that have already been scraped and skips them.

### Training the model
Just do:
```bash
python3 train.py
```
and the model will start the training process with 1000 epochs and all the entries in `entries.txt`.

### One-and-done method
The `run.py` script exists as a wrapper for all the other scripts. The idea is that you run a single Python command, and then you can walk away and let it do its thing. `python3 run.py --help` will tell you everything you need to know.

Here's how you'd set up a four-hour scrape followed by 1000 training epochs:
```bash
python3 run.py train-model --scrape-for 240 --num-epochs 1000
```