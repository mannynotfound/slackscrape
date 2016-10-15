#!/usr/bin/env python
from json_utils import load_json, dump_json
from slackclient import SlackClient
import operator
import os
import argparse

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory

config = load_json('./env.json')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--update', help = 'update channels', action="store_true")
    args = vars(ap.parse_args())

    slack_args = {
        'presence': 1
    }

    sc = SlackClient(config['token'])
    response = sc.api_call('users.list', **slack_args)
    users = response['members']

    for user in users:
        user_name = user['name']
        memb_path = ensure_dir('./output/users/members')
        user_path = '{}/{}.json'.format(memb_path, user_name)

        try:
            old_json = load_json(user_path)
            if not args['update']:
                print('Aready have user {}, skipping...'.format(user_name))
                continue
        except Exception as e:
            old_json = {}
            print('No existing messages, starting from scratch...')

        print('ADDING ', user_name)

        dump_json(user_path, user)
