# coding: utf-8
import requests
import re
from config import logger, XConfig
from utilities import record_data
import time

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,pt;q=0.8,zh-CN;q=0.7,zh;q=0.6',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Mobile Safari/537.36',
}

cookies = {
    'csrftoken': 'f07abcdea7036c89aa516b67c44cbf0b',  # 一年
    'tt_webid': '6510022945200047630',  # 10年
    '_ga': 'GA1.2.1807487632.1515732834',  # 两年
    '_gid': 'GA1.2.2105862598.1515732834',  # 一天
    '_ba': 'BA0.2-20171227-51225-0QOfevbdMYurWcR3FEl'  # 两年
}


def get_video_type():
    return ['subv_voice', 'subv_funny', 'subv_society',
            'subv_comedy', 'subv_life', 'subv_movie',
            'subv_entertainment', 'subv_cute', 'subv_game',
            'subv_boutique', 'subv_broaden_view', 'video_new']


def test_be_hot_data():
    params = {
        'tag': 'video_new',
        'ac': 'wap',
        'count': '20',
        'format': 'json_raw',
        'as': 'A135CAC5F8B2CC3',
        'cp': '5A58220C8CD32E1',
        'max_behot_time': '1515727802'
    }

    base_url = 'http://m.ixigua.com/list/'

    r = requests.get(base_url,
                     params=params,
                     headers=headers,
                     cookies=cookies, timeout=3)
    record_data(r.text, type='json')
    # print(r.apparent_encoding)  # 这个操作可能是非常耗时的，如果可以的话，记录一次下次就直接替换掉


def test_user_page(page_type='m'):
    """
    测试用户页面的请求情况和数据
    :param page_type: 如果是m表示是移动网页，如果是pc则表示是电脑版网页端。目前只支持移动端的网页
    :return:
    """
    if page_type != 'm':
        raise TypeError('this method only support mobile version')

    params = {
        'to_user_id': '5567057918',
        'format': 'html'
    }
    base_url = 'https://m.ixigua.com/video/app/user/home/'
    try:
        req = requests.get(base_url,
                           params=params,
                           # cookies=cookies,
                           headers=headers,
                           timeout=3)
        return 1
    except:
        return -1


def test_html_user_page():
    params = {
        'to_user_id': '5567057918',
        'format': 'json'
    }
    base_url = 'https://m.ixigua.com/video/app/user/home/'
    try:
        req = requests.get(base_url,
                           params=params,
                           cookies=cookies,
                           headers=headers,
                           timeout=3)
        return 1
    except:
        return -1


def test_video_page():
    """
    测试视频页面是不是有禁止访问的情况
    :return:
    """
    """setup"""
    video_url = 'https://www.ixigua.com/a{}'.format('6512907124689863172')
    error_counter = 0
    try:
        req = requests.get(video_url,
                           timeout=XConfig.TIMEOUT)
        if req.status_code == 403:
            error_counter += 1

    except requests.HTTPError:
        error_counter += 1
    except requests.Timeout:
        error_counter += 1
    except AttributeError:
        error_counter += 1


count = 0
all = 0
while True:
    all += 1
    res = test_user_page()
    if res == 1:
        count += 1
    print("{} / {}".format(count, all))
    time.sleep(0.5)
