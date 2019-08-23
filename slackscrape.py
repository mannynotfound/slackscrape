#!/usr/bin/env python
from json_utils import load_json, dump_json
from slackclient import SlackClient
import argparse

def get_messages(sc, slack_args, messages, filter_func):
    history = sc.api_call("channels.history", **slack_args)
    last_ts = history['messages'][-1]['ts'] if history['has_more'] else False
    filtered = list(filter(filter_func, history['messages']))
    all_messages = messages + filtered
    print('Fetched {} messages. {} Total now.'.format(len(filtered), len(all_messages)))

    return {
        'messages': all_messages,
        'last_ts': last_ts,
    }

def scrape_slack(token, slack_args, filter_func = lambda x: x):
    sc = SlackClient(token)
    results = get_messages(sc, slack_args, [], filter_func)

    while results['last_ts']:
        slack_args['latest'] = results['last_ts']
        results = get_messages(sc, slack_args, results['messages'], filter_func)

    print('Done fetching messages. Found {} in total.'.format(len(results['messages'])))
    return results['messages']

if __name__ == '__main__':
    config = load_json('./env.json')

    ap = argparse.ArgumentParser()
    ap.add_argument('-c', '--channel', help = 'channel id to scrape')
    ap.add_argument('-o', '--output', help = 'file to save out')
    args = vars(ap.parse_args())
    channel = args['channel']
    output = args['output']


    try:
        old_json = load_json(output)
    except Exception as e:
        old_json = []
        print('No existing messages, starting from scratch...')

    slack_args = {
        'channel': channel,
        'oldest': old_json[0]['ts'] if len(old_json) else '',
    }

    new_messages = scrape_slack(config['token'], slack_args)

    if len(new_messages):
        all_messages = new_messages + old_json
        dump_json(output, all_messages)
