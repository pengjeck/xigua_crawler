# coding: utf=8
# 只能说速度完全不行，就是个垃圾。
import requests
import time


def is_valid_proxy(proxy, timeout=1):
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

    xigua_url = 'https://m.ixigua.com/video/app/user/home/'
    xigua_params = {
        'to_user_id': '6597794261',
        'format': 'json',
    }
    try:
        beg_time = time.time()
        requests.get(url=xigua_url,
                     params=xigua_params,
                     headers=xigua_headers,
                     proxies=proxy,
                     timeout=timeout)
        return time.time() - beg_time
    except requests.exceptions.ProxyError:
        return 1000  # 意味着是完全没有用的代理
    except requests.Timeout:
        return 1000


def get_proxy():
    # 只获取一个
    url = 'http://api.ip.data5u.com/dynamic/get.html?order=9b46bfa48008e6bca51116605879324b&sep=3'
    try:
        req = requests.get(url,
                           timeout=15)
        if req.status_code != 200:
            return None

        # s = "http://{}".format(req.text.strip())
        s = 'http://{}'.format('60.186.158.171:42663')
        proxy = {
            'http': s,
            'https': s
        }
        time_cost = is_valid_proxy(proxy, timeout=3)
        print('time cost {}'.format(time_cost))
        if time_cost < 1.5:
            return proxy
        else:
            return None
    except requests.Timeout:
        return None
    except requests.HTTPError:
        return None
    except requests.ConnectionError:
        return None


print(get_proxy())
