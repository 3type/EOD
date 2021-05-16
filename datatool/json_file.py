import json


def load_json(file_path):
    with open(file_path) as fd:
        return json.load(fd)


def dump_json(file_path, obj):
    with open(file_path, 'w') as fd:
        json.dump(obj, fd, indent=4, ensure_ascii=False)
