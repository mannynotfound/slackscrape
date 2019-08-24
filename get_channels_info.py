#!/usr/bin/env python
from json_utils import *
from slackclient import SlackClient
import operator
import argparse

config = load_json('./env.json')

def all_channels_info(args):
    channel_args = {
        'exclude_archived': 0,
    }

    sc = SlackClient(config['token'])
    response = sc.api_call('channels.list', **channel_args)
    channels = response['channels']

    return channels

def store_channel_info(args):
    sc = SlackClient(config['token'])
    channels = all_channels_info(args)

    for idx, channel in enumerate(channels):
        chan_name = channel['name'].encode('utf-8')
        print('{} | {} - {} MEMBERS'.format(idx, chan_name, channel['num_members']))

        chan_path = ensure_dir('./output/channels/{}'.format(chan_name))
        info_path = ensure_dir('./output/channels/{}/info'.format(chan_name))
        output_path = '{}/{}.json'.format(info_path, chan_name)

        try:
            old_json = load_json(output_path)
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
            dump_json(output_path, channel_info)
        except Exception as e:
            print('ERROR DUMPING {}'.format(chan_name))
            print(e)

    return channels

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--update', help = 'update channels', action="store_true")
    args = vars(ap.parse_args())

    store_channel_info(args)

