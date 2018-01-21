"""
get user's id by m.ixigua.com
"""
# coding: utf-8
import requests
import json
import re
import sqlite3
from database import SqlXigua, AllUser
from config import XConfig, logging
from utilities import record_data
import time
from multiprocessing import Pool
from datetime import datetime
from user import User


# region 存储用户信息

class RequestPrepare:
    def __init__(self):
        self.db = AllUser()
        self.params = {
            'tag': 'video_new',
            'ac': 'wap',
            'count': '20',
            'format': 'json_raw',
            'as': 'A135CAC5F8B2CC3',
            'cp': '5A58220C8CD32E1',
            'max_behot_time': '1515727802'
        }

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'm.ixigua.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Mobile Safari/537.36',
        }
        self.cookies = {
            'csrftoken': 'f07abcdea7036c89aa516b67c44cbf0b',  # 一年
            'tt_webid': '6510022945200047630',  # 10年
            '_ga': 'GA1.2.1807487632.1515732834',  # 两年
            '_gid': 'GA1.2.2105862598.1515732834',  # 一天
            '_ba': 'BA0.2-20171227-51225-0QOfevbdMYurWcR3FEl'  # 两年
        }
        self.base_url = 'http://m.ixigua.com/list/'
        self.categorys = ['subv_voice', 'subv_funny', 'subv_society',
                          'subv_comedy', 'subv_life', 'subv_movie',
                          'subv_entertainment', 'subv_cute', 'subv_game',
                          'subv_boutique', 'subv_broaden_view', 'video_new']


rp = RequestPrepare()


def get_now_min_behot_time():
    return int(time.time())


def extract_user_id(source_open_url):
    """
    extract the user id from given user's id
    :param source_open_url: "sslocal://profile?refer=video&uid=6115075278" example
    :return:
    """
    if source_open_url[10:17] != 'profile':
        return None

    try:
        res = re.search("\d+$", source_open_url).group(0)
        return res.strip()
    except (AttributeError, KeyError):
        return None


def run_pool(category):
    rp.params['tag'] = category
    user_ids = []
    try:
        r = requests.get(rp.base_url,
                         params=rp.params,
                         headers=rp.headers,
                         timeout=XConfig.TIMEOUT,
                         cookies=rp.cookies)
        data = json.loads(r.text.encode('utf-8'), encoding='ascii')
        for item in data['data']:
            user_id = extract_user_id(item['source_open_url'])
            if user_id is None:
                continue
            user_ids.append(user_id)
    except requests.Timeout:
        logging.error('timeout occur when requesting user ids')
    except json.JSONDecodeError:
        logging.error('error occur when decoding requests.text to json. r={}/category={}'.format(r, category))
    except requests.HTTPError:
        logging.error('http error occur when requesting user ids')
    except requests.ConnectionError:
        logging.error('connection error occur when requesting user ids')
    return list(set(user_ids))


def run(times):
    now_time_stamp = get_now_min_behot_time()

    all_count = 0
    for i in range(times):
        max_behot_time = int(now_time_stamp - (604800 / 2 - (604800 / times) * i))
        rp.params['max_behot_time'] = max_behot_time
        with Pool(12) as p:
            user_ids_s = p.map(run_pool, rp.categorys)
        count = 0
        for user_ids in user_ids_s:
            for user_id in user_ids:
                try:
                    u = User(user_id)
                    rp.db.insert(u, is_commit=False)
                    count += 1
                except sqlite3.IntegrityError:
                    logging.info('[{}] {} has appear in database!'.format(datetime.now(), user_id))
        rp.db.conn.commit()
        all_count += count
        print("{}th => {} / {}".format(i + 1, count, all_count))

# endregion 存储用户信息
