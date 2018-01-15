"""
toolbox
"""
# coding: utf-8
import json


def record_data(data, filename='test.json', encoding='utf-8'):
    """
    record lastest data before exception appear.
    """
    if isinstance(data, str):
        with open(filename, 'w', encoding=encoding) as f:
            f.write(data)
    elif isinstance(data, dict):
        with open(filename, 'w', encoding=encoding) as f:
            json.dump(data, f)
    else:
        with open(filename, 'w', encoding=encoding) as f:
            f.write(str(data))
