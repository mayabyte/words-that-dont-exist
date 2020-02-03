import gpt_2_simple as gpt2
import os
import json
import random
import shutil

def download_model(model_name):
    if not os.path.isdir(os.path.join('models', model_name)):
        print(f'Downloading {model_name} model...')
        gpt2.download_gpt2(model_name=model_name)
    else:
        print(f'Model {model_name} already downloaded. Skipping.')

def entry_to_string(entry):
    definitions_string = '\n'.join(f'{i+1}: {defi}' for i, defi in enumerate(entry['defs']))
    pos = random.choice(entry['pos']).strip()
    ipa = entry['ipa'][0]
    return f'{entry["word"]} ({pos})\n/{ipa}/\n\n{definitions_string}\n\n'

def write_pretty_dictionary():
    file_name = 'dictionary.txt'
    if os.path.isfile(file_name):
        os.remove(file_name)

    entry_strings = []
    failed_counter = 0
    with open('entries.txt', 'r') as dict_entries:
        for entry_json_str in dict_entries:
            entry = json.loads(entry_json_str)
            try:
                entry_strings.append(entry_to_string(entry))
            except Exception as e:
                failed_counter += 1
                continue

    if failed_counter > 0:
        print(f'Failed to map {failed_counter} incomplete entries')

    random.shuffle(entry_strings)
    with open(file_name, 'w+') as dest:
        for entry in entry_strings:
            dest.write(entry)

def train_model(model_name, fresh=False, num_epochs=1000):
    if fresh:
        shutil.rmtree('checkpoint')
    sess = gpt2.start_tf_sess()
    gpt2.finetune(
        sess,
        'dictionary.txt',
        model_name=model_name,
        steps=num_epochs
    )
    gpt2.generate(sess)

def generate_output(length=1000):
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess)
    output = gpt2.generate(sess, return_as_list=True)[:length]
    for o in output:
        print(o)