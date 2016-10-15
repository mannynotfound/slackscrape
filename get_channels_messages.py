#!/usr/bin/env python
from json_utils import load_json, dump_json
from slackscrape import scrape_slack
from slackclient import SlackClient
import argparse
import operator
import os

config = load_json('./env.json')

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-a', '--archived', help = 'include archived channels', action="store_true")
    ap.add_argument('-u', '--update', help = 'update channels', action="store_true")
    args = vars(ap.parse_args())

    slack_args = {
        'exclude_archived': 0 if args['archived'] else 1,
    }

    sc = SlackClient(config['token'])
    response = sc.api_call('channels.list', **slack_args)
    channels = response['channels']

    sorted_channels = sorted(channels, key=lambda x: x['num_members'], reverse=True)

    for idx, channel in enumerate(sorted_channels):
        chan_name = channel['name']
        print('{} | {} - {} MEMBERS'.format(idx, chan_name, channel['num_members']))
        chan_path = ensure_dir('./output/channels/{}'.format(chan_name))
        msg_path = ensure_dir('./output/channels/{}/messages'.format(chan_name))
        output = './output/channels/{}/messages/{}.json'.format(chan_name, chan_name)

        try:
            old_json = load_json(output)
            if not args['update']:
                print('Aready have messages, skipping...')
                continue
        except Exception as e:
            old_json = []
            print('No existing messages, starting from scratch...')

        slack_args = {
            'channel': channel['id'],
            'oldest': old_json[0]['ts'] if len(old_json) else '',
        }

        new_messages = scrape_slack(config['token'], slack_args)

        if len(new_messages):
            all_messages = new_messages + old_json
            dump_json(output, all_messages)
