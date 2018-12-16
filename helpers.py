import os
from yaml import safe_dump


def store_index(dic):
    stream = open('./output/index.yaml', 'w')
    safe_dump(dic, stream=stream, default_flow_style=False, explicit_start=True)

def ensure_directory(dir):
    try:
        os.mkdir(dir)
    except OSError:
        pass
