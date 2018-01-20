"""
toolbox
"""
# coding: utf-8
import json


def record_data(data, type='json', filename='default'):
    """
    record lastest data before exception appear.
    """
    if filename == 'default':
        if type == 'json':
            filename = 'json.json'
        elif type == 'html':
            filename = 'html.html'
        else:
            raise ValueError('record data s file type must be json or html')

    if isinstance(data, str):
        with open(filename, 'w') as f:
            f.write(data)
    elif isinstance(data, dict):
        with open(filename, 'w') as f:
            json.dump(data, f)
    else:
        with open(filename, 'w') as f:
            f.write(str(data))
