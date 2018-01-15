"""
module for single track
说明：移动网页和pc网页显示的粉丝数目不一致，而且移动版的网页不显示该用户的关注数目
"""
# coding: utf-8

import requests
import re
import logging
import time
import pickle


def get_content(url):
    """
    获取包含播放次数的原始内容
    :param url:
    :return:
    """
    try:
        r = requests.get(url)
        return r.text
    except:
        logging.exception("request error!!!")
        return None


def play_count(content):
    """
    获取播放次数
    :param content:
    :return: 失败返回 -1
    """
    try:
        m = re.search("videoPlayCount: \d+", content)
        return int(m.group(0)[16:])
    except:
        logging.exception("cannot get play count {}".format(content))
        return -1


def track(video_url, times=100, time_span=60):
    res = []
    for i in range(times):
        content = get_content(video_url)
        # print(content)
        count = play_count(content)
        if count == -1:
            return []
        else:
            res.append(count)
            print(count)
        time.sleep(time_span)
    return res


# 一分钟记录一次，跟踪100次，大概1.5个小时
counts = track('https://www.ixigua.com/a6507400916369408519/#mid=73132143386')
with open('track.pkl', 'wb') as f:
    pickle.dump(counts, f)
