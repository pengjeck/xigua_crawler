# coding: ** utf-8 **

import io
import json


def save_json_to_file(json_obj, filename, directory='data'):
    """
    把获取到的json数据写到一个json文件里面
    :param json_obj:
    :param filename:
    :param directory: 目录，默认为data目录
    :return: 文件地址
    """
    file = '{}/{}.json'.format(directory, filename)
    with io.open(file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(json_obj, ensure_ascii=False))
    return file
