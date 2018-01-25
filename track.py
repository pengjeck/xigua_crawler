# coding: utf-8

# region >>>>>>>>>>> sampling >>>>>>>>>>
"""
总流程：
    1. 对每一个用户请求其follower数
    2. 存储到数据库（原）中。
    3. 根据follower数排序。
    4. 使用分层抽样的方法抽取1000个用户.

    1. 一共17473个用户，从数据库中把用户的id全部取出，加载到内存。
    2. 30个为一组，pool参数设置为20;
    3. 判断id是否有效->请求用户页面。
    4. 判断页面是否请求成功->解析页面数据。
    5. 判断页面解析是否成功->更新数据库
    6. 取出所有的用户数据，根据follower数进行排序分层
    7. 使用分层抽样的方法抽取1000个用户。
    8. 将新抽取的用户存入新的数据中。
"""
# endregion <<<<<<<<<<< sampling <<<<<<<<<<

import requests
from itertools import product
import json
from config import logger, XConfig
from multiprocessing import Pool
from database import SqlXigua
from xigua import VideoPage
from tempor import Tempor
from datetime import datetime
import time
import sqlite3
from apscheduler.schedulers.blocking import BlockingScheduler
import sys
import atexit


class Instance:
    """
    抽取17000个用于跟踪的用户：真的要这么多吗？
    """

    def __init__(self):
        self._base_user_url = 'https://m.ixigua.com/video/app/user/home/'
        self.new_videos = []
        self._pool_size = 70
        self.headers = XConfig.HEADERS_1
        self.proxy = None
        self.proxies_use = False

        # 已经把第一次的记录放进去了
        self.get_new_videos()

    @staticmethod
    def _url_join(base_url, params):
        """
        连接url和params
        :param base_url:
        :param params:
        :return:
        """
        if not isinstance(params, dict):
            logger.error('url params must be dictionary')

        if base_url[-1] != '?':
            base_url += '?'
        for keys in params:
            item = "{}={}&".format(keys, params[keys])
            base_url += item
        return base_url[:-1]

    def get_new_videos(self):
        """
        获取最新的视频（全量搜索）
        :return:
        """
        for i in range(int(len(all_user) / self._pool_size)):
            with Pool(self._pool_size) as p:
                part_users = all_user[i * self._pool_size: (i + 1) * self._pool_size]
                results = p.map(self._get_new_video, part_users)

            # 是否已经更换过一次代理了
            need_change_proxy = False
            for res in results:
                if res['code'] == 1:
                    need_change_proxy = True

                if len(res['video_ids']) != 0:
                    self.new_videos.extend(res['video_ids'])

            if need_change_proxy:
                if self.proxies_use:
                    if self.test_no_proxy():
                        self.proxies_use = False
                    else:
                        proxy = Instance.get_proxies(count=4)
                        if proxy is None:
                            self.proxy = Instance.get_proxies(count=4)
                            if self.proxy is None:
                                self.proxies_use = False
                            else:
                                self.proxies_use = True
                        else:
                            self.proxy = proxy
                            self.proxies_use = True
                else:
                    proxy = Instance.get_proxies(count=4)
                    if proxy is None:
                        self.proxy = Instance.get_proxies(count=4)
                        if self.proxy is None:
                            self.proxies_use = False
                        else:
                            self.proxies_use = True
                    else:
                        self.proxy = proxy
                        self.proxies_use = True

        for video_id in self.new_videos:
            t = Tempor(video_id, datetime.now(),
                       views=0, likes=0, dislikes=0,
                       comments=0)
            try:
                db.insert(t, is_commit=False)
            except sqlite3.InterfaceError:
                print(video_id)
        db.conn.commit()

    @staticmethod
    def get_proxies(count=6):
        base_url = 'http://www.mogumiao.com/proxy/api/get_ip_al'
        params = {
            'appKey': '7f52750cc46548b7b316bfaf73792f70',
            'count': count,
            'expiryDate': 5,
            'format': 1
        }
        try:
            r = requests.get(base_url, params)
            if r.status_code != 200:
                logger.error('cannot get proxy from {}'.format(base_url))
                return

            data = json.loads(r.text)
            if data['code'] != '0':
                logger.error('{} server error'.format(base_url))
                return
            proxy_pool = []
            for item in data['msg']:
                proxy = 'http://{}:{}'.format(item['ip'], item['port'])
                proxy_pool.append({
                    'http': proxy,
                    'https': proxy
                })

            # 选择最好的代理。
            proxy_index = Instance.get_best_proxy(proxy_pool)
            if proxy_index == -1:
                return None
            else:
                return proxy_pool[proxy_index]
        except (requests.HTTPError, requests.ConnectionError,
                requests.Timeout, json.JSONDecodeError):
            logger.error('network error when get proxy error!')
            return
        except KeyError:
            logger.error('proxies decode error')
            return

    @staticmethod
    def get_best_proxy(proxies):
        # 给代理评分
        min_index_proxy = -1
        min_score = 10000
        for (i, proxy) in enumerate(proxies):
            score = Instance.is_valid_proxy(proxy)
            if score == 1000:
                continue
            else:
                if score < min_score:
                    min_index_proxy = i
                    min_score = score

        return min_index_proxy

    @staticmethod
    def is_valid_proxy(proxy, timeout=1.5):
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

    @staticmethod
    def test_no_proxy(timeout=1):
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
            req = requests.get(url=xigua_url,
                               params=xigua_params,
                               headers=xigua_headers,
                               timeout=timeout)
            if req.status_code != 403:
                return True
            else:
                return False
        except requests.Timeout:
            return False

    def _get_new_video(self, user_id):
        """
        解析用户页面
        :param user_id:
        :return: User对象
        """
        # headers = XConfig.HEADERS_1

        base_user_url = 'http://m.365yg.com/video/app/user/home/'
        params = {
            'to_user_id': user_id,
            'device_id': '42136171291',
            'format': 'json',
            'app': 'video_article',
            'utm_source': 'copy_link',
            'utm_medium': 'android',
            'utm_campaign': 'client_share',
        }
        res = {
            'code': 0,
            'video_ids': []
        }
        try:
            if not self.proxies_use:
                req = requests.get(base_user_url,
                                   params=params,
                                   headers=self.headers,
                                   timeout=XConfig.TIMEOUT)

            else:
                req = requests.get(base_user_url,
                                   params=params,
                                   proxies=self.proxy,
                                   headers=self.headers,
                                   timeout=XConfig.TIMEOUT)

            if req.status_code == 403:
                res['code'] = 1  # 意味着要更换代理
                return res

            data = json.loads(req.text.encode('utf-8'), encoding='ascii')
            if data['message'] != 'success':
                logger.info('do not success when request user page!')
                res['code'] = 2  # 西瓜服务器出现了问题
                return res

            now = time.time()
            for item_v in data['data']:
                try:
                    # 五分钟以内上传的视频都可以算作新视频
                    if now - int(item_v['publish_time']) < 360:
                        video_id = item_v['group_id_str']
                        res['video_ids'].append(video_id)
                except KeyError as e:
                    logger.error('cannot parse video_id. reason:{}'.format(e))
                    pass

            return res
        except requests.Timeout:
            logger.error('time out request user page')
            res['code'] = 3  # 网络问题
            return res
        except requests.ConnectionError:
            logger.error('connection error occur when request user ')
            res['code'] = 3
            return res
        except requests.HTTPError:
            logger.error('http error when request user page')
            res['code'] = 3
            return res
        except json.JSONDecodeError as e:
            logger.error('cannot decode response data to json object {}'.format(e))
            res['code'] = 3
            return res
        except KeyError as e:
            logger.error('cannot parse user info. reason:{}'.format(e))
            res['code'] = 4  # 数据解析出现错误
            return res

    def track(self):
        now = datetime.now()
        with Pool(self._pool_size) as p:
            if self.proxies_use:
                video_pages = p.starmap(VideoPage, product(self.new_videos, self.proxy))
            else:
                video_pages = p.map(VideoPage, self.new_videos)

        # 是否需要换代理的flag
        need_change_proxy = False
        for video_page in video_pages:
            # 说明出了问题
            if video_page.is_finish != 1:
                if video_page.is_finish == 3:
                    need_change_proxy = True
            else:
                t = Tempor(video_page.video_id, now,
                           video_page.views, video_page.likes,
                           video_page.dislikes, video_page.comments)
                db.insert(t, is_commit=False)
        db.conn.commit()

        if need_change_proxy:
            if self.proxies_use:
                if self.test_no_proxy():
                    self.proxies_use = False
                else:
                    proxy = Instance.get_proxies()
                    if proxy is None:
                        self.proxy = Instance.get_proxies()
                        if self.proxy is None:
                            self.proxies_use = False
                        else:
                            self.proxies_use = True
                    else:
                        self.proxy = proxy
                        self.proxies_use = True
            else:
                proxy = Instance.get_proxies()
                if proxy is None:
                    self.proxy = Instance.get_proxies()
                    if self.proxy is None:
                        self.proxies_use = False
                    else:
                        self.proxies_use = True
                else:
                    self.proxy = proxy
                    self.proxies_use = True


def tick():
    job_instance.track()


def single_scheduler():
    global job_instance
    global all_user
    beg = time.time()
    job_instance = Instance()
    del all_user
    if len(job_instance.new_videos) < 120:
        print(
            'find cost {}; video number too small = {}, exit.'.format(time.time() - beg, len(job_instance.new_videos)))
        return
    else:
        print('find cost {}; there are {} video will be track in this process.'.format(time.time() - beg,
                                                                                       len(job_instance.new_videos)))
        scheduler = BlockingScheduler()
        # scheduler.add_executor('processpool')
        scheduler.add_job(tick, 'interval', seconds=XConfig.TRACK_SPAN)
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print('process has exit!!!')
            scheduler.shutdown()


def load_all_user():
    res = []
    with open(XConfig.USER_IDS_FILE, 'r') as f:
        for line in f:
            res.append(line[:-1])
    return res


def at_exit():
    global db
    print('process exited!!')
    db.conn.close()


# region test track
# video_ids = ["6513037259028038158",
#              "6513433089388053000",
#              "6513472844448402702",
#              "6513471677307814403",
#              "6513150551188832775",
#              "6513142054137102855",
#              "6513472347482096141",
#              "6513122203721007620",
#              "6513471946015900168",
#              "6513472157815669252"]
# index = 0
# db = SqlXigua(index)
# all_user = load_all_user()
#
# i = Instance()
# i.new_videos = video_ids
# i.track()
# endregion

atexit.register(at_exit)

job_instance = None
all_user = load_all_user()
index = int(sys.argv[1])
# index = 0
db = SqlXigua(index)
single_scheduler()
