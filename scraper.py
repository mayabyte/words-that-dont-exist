import httpx
import json
import asyncio
import backoff
import time
from random import shuffle
from bs4 import BeautifulSoup
from tqdm import tqdm, trange
from pprint import pprint

words_list_url = 'https://raw.githubusercontent.com/dwyl/english-words/master/words_dictionary.json'
merriam_webster_definition_url = 'https://www.merriam-webster.com/dictionary/{}'

def load_words(filter_existing_entries=True):
    words = None
    try:
        with open('words.txt', 'r') as word_file:
            words = list(json.loads(word_file.read()))
    except IOError:
        print("Words file not found, downloading...")
        words_req = httpx.get(words_list_url)
        f = open('words.txt', 'w+')
        f.write(words_req.text)
        words = list(words_req.json())
    words = set(filter(lambda x: len(x) > 2, words))
    print('Words loaded.')

    if filter_existing_entries:
        try:
            with open('entries.txt', 'r') as entry_file:
                num_total_words = len(words)
                existing_words = {json.loads(line)['word'] for line in entry_file}
                words = words.difference(existing_words)
                print('Removed {} already-scraped words.'.format(num_total_words-len(words)))
        except Exception as e:
            pass # no entries file, nothing to do

    # shuffle the list to ensure good alphabetic distribution at all times
    words = list(words)
    shuffle(words)

    return words


@backoff.on_exception(
    backoff.fibo,
    (httpx.HTTPError),
    jitter=backoff.random_jitter,
    max_time=35,
)
async def get_word_def__merriam_webster(client, word):
    try:
        response = await client.get(merriam_webster_definition_url.format(word))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('h1', class_='hword').string.strip();
        assert(title == word)

        pos = clean_str_list([e.string for e in soup.find_all('span', class_='fl')])
        assert(len(pos) > 0)

        ipa = clean_str_list([
            e.next_sibling.string or list(e.next_sibling.strings)[0]
            for e in soup.find_all('span', class_='first-slash')
        ])
        assert(len(ipa) > 0)

        for e in soup.find_all(class_='mw_t_bc'):
            e.decompose()
        definitions = [' '.join(''.join(d.strings).strip().split()).strip() for d in soup.find_all('span', class_='dtText')]
        assert(len(definitions) > 0)

        entry = {
            'word': word,
            'pos': pos,
            'ipa': ipa,
            'defs': definitions
        }
        return entry
    except httpx.HTTPError as e:
        raise e
    except Exception as e:
        return None

async def try_get(client, word):
    try:
        return await get_word_def__merriam_webster(client, word)
    except Exception as e:
        return None

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def clean_str_list(lst):
    return list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), lst)))

async def get_all_definitions(runtime=None):
    words = load_words()
    chunk_size = 1500
    start_time = time.time()

    print("Scraping dictionary entries...")
    if runtime is None:
        print("(This takes a long time. Scraped entries are saved to file after each chunk, so feel free to exit early if you feel you have enough data.)")

    for i, word_chunk in enumerate(tqdm(list(chunks(words, chunk_size)), desc='Total')):
        if runtime and (time.time()-start_time)/60 > runtime:
            print('Specified runtime has elapsed. Stopping.')
            break
        async with httpx.AsyncClient() as client:
            pending = list(try_get(client, w) for w in word_chunk)
            finished = filter(lambda x: x is not None,
                [await r for r in tqdm(
                    asyncio.as_completed(pending),
                    total=chunk_size,
                    desc='Chunk '+str(i+1),
                    leave=False)
                ])
            save_dictionary_entries(finished)

def save_dictionary_entries(entries):
    with open('entries.txt', 'a') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')

if __name__ == '__main__':
    asyncio.run(get_all_definitions())