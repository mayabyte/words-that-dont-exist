import gpt_2_simple as gpt2
import os
import json
import random

model_name = '124M'
if not os.path.isdir(os.path.join('models', model_name)):
    print(f'Downloading {model_name} model...')
    gpt2.download_gpt2(model_name=model_name)

def entry_to_string(entry):
    definitions_string = '\n'.join(f'{i+1}: {defi}' for i, defi in enumerate(entry['defs']))
    pos = random.choice(entry['pos']).strip()
    ipa = entry['ipa'][0]
    return f'{entry["word"]} ({pos})\n/{ipa}/\n\n{definitions_string}\n\n'

print('Writing dictionary entries...')

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

print('done.\n\nTraining model...')

sess = gpt2.start_tf_sess()
gpt2.finetune(
    sess,
    file_name,
    model_name=model_name,
    steps=1000
)
gpt2.generate(sess)