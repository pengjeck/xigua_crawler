# coding: utf-8
import requests
import re
import json
from config import logger, XConfig
from utilities import record_data
import time
import multiprocessing

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


# region test the video page will kill ip address
def parse_views(data):
    """parse view count to .views"""
    m = re.search("videoPlayCount: \d+", data)
    return int(m.group(0)[16:])


def parse_likes(data):
    """parse like count to .likes"""
    raw_likes = re.search('diggCount: \d+', data).group(0)
    return int(raw_likes[11:])


def parse_dislikes(data):
    """parse dislike count to .dislikes"""
    raw_dislikes = re.search('buryCount: \d+', data).group(0)
    return int(raw_dislikes[11:])


def parse_comments(data):
    """解析评论数据"""
    raw_comments = re.search('count: \d+', data).group(0)
    return int(raw_comments[7:])


def test_video_page():
    """
    测试视频页面是不是有禁止访问的情况
    :return:
    """
    """setup"""
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }

    video_url = 'https://www.ixigua.com/a{}'.format('6512907124689863172')

    try:
        req = requests.get(video_url,
                           headers=headers,
                           timeout=XConfig.TIMEOUT)
        if req.status_code == 403:
            return 1
        parse_views(req.text)
        parse_likes(req.text)
        parse_dislikes(req.text)
        parse_comments(req.text)
        return 0
    except requests.ConnectionError:
        return 1
    except requests.HTTPError:
        return 1
    except requests.Timeout:
        return 1
    except AttributeError:
        return 1


# endregion test the video will kill ip address


# region test http://www.mogumiao.com proxy server

def get_proxy(count):
    base_url = 'http://www.mogumiao.com/proxy/api/get_ip_al'
    params = {
        'appKey': '7f52750cc46548b7b316bfaf73792f70',
        'count': count,
        'expiryDate': 5,
        'format': 1
    }
    res = []
    try:
        r = requests.get(base_url, params)
        # r = requests.get(url)
        if r.status_code != 200:
            logger.error('cannot get proxy from {}'.format(base_url))
            return []
        data = json.loads(r.text)
        print(data)
        if data['code'] != '0':
            logger.error('{} server error'.format(base_url))
            return []
        for pro in data['msg']:
            if 'ip' not in pro or 'port' not in pro:
                continue

            proxy = 'http://{}:{}'.format(pro['ip'], pro['port'])
            res.append({
                'http': proxy,
                'https': proxy
            })
        return res
    except (requests.HTTPError, requests.ConnectionError,
            requests.Timeout, json.JSONDecodeError):
        return []
    except KeyError:
        return res


def valid_proxy(raw_proxy, timeout=2):
    """
    :param raw_proxy:
    :param timeout:
    :return:
    """
    xigua_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'cache-control': 'max-age=0',
        'referer': 'https',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Mobile Safari/537.36',
    }
    xigua_params = {
        'to_user_id': '6597794261',
        'format': 'html',
    }

    xigua_url = "https://m.ixigua.com/video/app/user/home/"
    res = []
    for proxy in raw_proxy:
        try:
            requests.get(url=xigua_url,
                         params=xigua_params,
                         headers=xigua_headers,
                         proxies=proxy,
                         timeout=timeout)
            res.append(proxy)
        except requests.exceptions.ProxyError:
            logger.error('proxy invalidity')

    return res


def get_single_proxy():
    base_url = 'http://www.mogumiao.com/proxy/api/get_ip_al'
    params = {
        'appKey': '7f52750cc46548b7b316bfaf73792f70',
        'count': 1,
        'expiryDate': 5,
        'format': 1
    }
    res = {}
    try:
        r = requests.get(base_url, params)
        # r = requests.get(url)
        if r.status_code != 200:
            logger.error('cannot get proxy from {}'.format(base_url))
            return []
        data = json.loads(r.text)
        if data['code'] != '0':
            logger.error('{} server error'.format(base_url))
            return res
        proxy = 'http://{}:{}'.format(data['msg'][0]['ip'], data['msg'][0]['port'])
        res['http'] = proxy
        res['https'] = proxy
        return res
    except (requests.HTTPError, requests.ConnectionError,
            requests.Timeout, json.JSONDecodeError):
        return {}
    except KeyError:
        return res


def is_valid_proxy(proxy, timeout=2):
    """
    :param proxy:
    :param timeout:
    :return:
    """
    xigua_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'cache-control': 'max-age=0',
        'referer': 'https',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Mobile Safari/537.36',
    }

    xigua_url = 'http://m.365yg.com/video/app/user/home/'
    xigua_params = {
        'to_user_id': '6597794261',
        'device_id': '42136171291',
        'format': 'json',
        'app': 'video_article',
        'utm_source': 'copy_link',
        'utm_medium': 'android',
        'utm_campaign': 'client_share',
    }
    try:
        requests.get(url=xigua_url,
                     params=xigua_params,
                     headers=xigua_headers,
                     proxies=proxy,
                     timeout=timeout)
        return True
    except requests.exceptions.ProxyError:
        return False
    except requests.Timeout:
        return False


# endregion


# region change ua

def test_ua_page(ua):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': ua
    }

    video_url = 'https://www.ixigua.com/a{}'.format('6512907124689863172')

    try:
        req = requests.get(video_url,
                           headers=headers,
                           timeout=XConfig.TIMEOUT)
        if req.status_code == 403:
            return 1
        parse_views(req.text)
        parse_likes(req.text)
        parse_dislikes(req.text)
        parse_comments(req.text)
        return 0
    except requests.ConnectionError:
        return 1
    except requests.HTTPError:
        return 1
    except AttributeError:
        return 1


# endregion
#
# f = open('tool/1000-pc.log', 'r')
# count = 0
# times = 0
# ua = f.readline().strip()
# while True:
#     times += 1
#     state_code = test_ua_page(ua)
#     if state_code == 1:
#         ua = f.readline().strip()
#         count += 1
#     print("error / times = {} / {}".format(count, times))
#     # time.sleep(1)


count = 0
times = 0
ua_index = 1


def get_ua():
    global ua_index
    if ua_index == 1:
        return 'Mozilla/5.0'
    elif ua_index == 2:
        return 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    elif ua_index == 3:
        return 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
    elif ua_index == 4:
        return 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.34 (KHTML, like Gecko) Qt/4.8.2'
    elif ua_index == 5:
        return 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36'


while True:
    times += 1
    res = test_ua_page(get_ua())
    if res == 1:
        count += 1
        if ua_index == 1:
            ua_index = 2
        elif ua_index == 2:
            ua_index = 3
        elif ua_index == 3:
            ua_index = 4
        elif ua_index == 4:
            ua_index = 5
        elif ua_index == 5:
            ua_index = 1
    print("error / times = {} / {}".format(count, times))
    # time.sleep(1)
