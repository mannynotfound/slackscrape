import re
from json_utils import load_json
import operator
import os
import pprint
from sets import Set
from itertools import islice

def take(n, iterable):
    return list(islice(iterable, n))

allowed_chars = Set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')

master_count = {}

def add_hit(channel, hit_type, hit):
    if not master_count.get(channel):
        master_count[channel] = {
            'emojis': {},
            'emojis_reactions': {},
        }

    if not master_count.get(channel).get(hit_type).get(hit):
        master_count[channel][hit_type][hit] = 0

    master_count[channel][hit_type][hit] += 1


def filter_emojis(text):
    return Set(text.replace(':', '')).issubset(allowed_chars) and len(text) > 2

for idx, dump in enumerate(os.listdir('./output/channels')):
    try:
        messages = load_json('./output/channels/{}/messages/{}.json'.format(dump, dump))
        print('ANALYZING {}'.format(dump))
    except Exception as e:
        print('ERROR GETTING MESSSAGES IN {}'.format(dump))
        print(e)
        continue

    for message in messages:
        emojis = []
        emojis_reactions = []

        if message.get('text'):
            text_emojis = re.findall('\:.*?\:', message['text'])
            text_emojis = list(filter(lambda x: filter_emojis(x), text_emojis))
            if len(text_emojis):
                text_emojis = list(map(lambda x: x.replace(':', ''), text_emojis))
                # print('TEXT EMOJIS =>')
                # print(text_emojis)
                emojis += text_emojis

        if message.get('reactions'):
            for reaction in message.get('reactions'):
                emojis_reactions.append(reaction['name'])

            # print('REACTION EMOJIS =>')
            # print(emojis_reactions)

        for emoji in emojis:
            add_hit(dump.replace('.json', ''), 'emojis', emoji)

        for reaction in emojis_reactions:
            add_hit(dump.replace('.json', ''), 'emojis_reactions', reaction)


master_emojis_count = {
    'emojis': {},
    'emojis_reactions': {},
}

def add_emoji_hit(hit_type, hit, total):
    if not master_emojis_count.get(hit_type).get(hit):
        master_emojis_count[hit_type][hit] = 0

    master_emojis_count[hit_type][hit] += total

for channel in master_count:
    for emoji in master_count[channel]['emojis']:
        add_emoji_hit('emojis', emoji, master_count[channel]['emojis'][emoji])
    for reaction in master_count[channel]['emojis_reactions']:
        add_emoji_hit('emojis_reactions', reaction, master_count[channel]['emojis_reactions'][reaction])


sorted_emojis = sorted(master_emojis_count['emojis'].items(), key=operator.itemgetter(1), reverse=True)
sorted_reactions = sorted(master_emojis_count['emojis_reactions'].items(), key=operator.itemgetter(1), reverse=True)

pp = pprint.PrettyPrinter(indent=2)

print('TOP EMOJIS =>')
pp.pprint(sorted_emojis[:50])
print('')
print('TOP REACTIONS =>')
pp.pprint(sorted_reactions[:50])
