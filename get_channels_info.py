#!/usr/bin/env python
from json_utils import *
from slackscrape import scrape_slack
from slackclient import SlackClient
import operator
import argparse

config = load_json('./env.json')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--update', help = 'update channels', action="store_true")
    args = vars(ap.parse_args())

    channel_args = {
        'exclude_archived': 0,
    }

    sc = SlackClient(config['token'])
    response = sc.api_call('channels.list', **channel_args)
    channels = response['channels']

    for idx, channel in enumerate(channels):
        chan_name = channel['name'].encode('utf-8')
        print('{} | {} - {} MEMBERS'.format(idx, chan_name, channel['num_members']))

        chan_path = ensure_dir('./output/channels/{}'.format(chan_name))
        info_path = ensure_dir('./output/channels/{}/info'.format(chan_name))

        try:
            old_json = load_json('{}/{}.json'.format(info_path, chan_name))
            if not args['update']:
                print('Already have channel {}, skipping ...'.format(chan_name))
                continue
        except Exception as e:
            print('No existing channel {} info, fetching ...'.format(chan_name))

        slack_args = {
            'channel': channel['id'],
        }

        channel_info = sc.api_call('channels.info', **slack_args)
        try:
            dump_json('{}/{}.json'.format(info_path, chan_name), channel_info)
        except Exception as e:
            print('ERROR DUMPING {}'.format(chan_name))
            print(e)
