import json


def read_json(file_path: str):
    """read json file
    """
    with open(file_path) as f:
        return json.load(f)


def read_file(file_name: str):
    """read file
    """
    with open(file_name) as f:
        return f.read()
    