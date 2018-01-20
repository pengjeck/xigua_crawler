# coding: utf-8

import requests
from config import logger
import json

"""
PROXIES = {
    'http': 'socks5://127.0.0.1:1081',
    'https': 'socks5://127.0.0.1:1081'
}
"""


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


import time

beg = time.time()
proxies = get_single_proxy()
print(proxies)
print(is_valid_proxy(proxies))
print(time.time() - beg)
