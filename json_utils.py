import io
import json
from operator import itemgetter
from datetime import datetime
import time

def load_json(path):
    with io.open(path, encoding='utf-8') as f:
        return json.loads(f.read())

def dump_json(path, data):
    with open(path, mode='w') as f:
        json.dump(data, f, indent = 2)
