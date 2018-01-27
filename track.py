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

            for res in results:
                if len(res['video_ids']) != 0:
                    self.new_videos.extend(res['video_ids'])

        for video_id in self.new_videos:
            t = Tempor(video_id, datetime.now(),
                       views=0, likes=0, dislikes=0,
                       comments=0)
            try:
                db.insert(t, is_commit=False)
            except sqlite3.InterfaceError:
                print(video_id)
        db.conn.commit()

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
        video_ids = []
        try:
            req = requests.get(base_user_url,
                               params=params,
                               headers=self.headers,
                               timeout=XConfig.TIMEOUT)

            if req.status_code == 403:
                pass

            data = json.loads(req.text.encode('utf-8'), encoding='ascii')
            if data['message'] != 'success':
                logger.info('do not success when request user page!')
                pass

            now = time.time()
            for item_v in data['data']:
                try:
                    if now - int(item_v['publish_time']) < 360:
                        video_id = item_v['group_id_str']
                        video_ids.append(video_id)
                except KeyError as e:
                    logger.error('cannot parse video_id. reason:{}'.format(e))
                    pass

            return video_ids
        except requests.Timeout:
            logger.error('time out request user page')
            return video_ids
        except requests.ConnectionError:
            logger.error('connection error occur when request user ')
            return video_ids
        except requests.HTTPError:
            logger.error('http error when request user page')
            return video_ids
        except json.JSONDecodeError as e:
            logger.error('cannot decode response data to json object {}'.format(e))
            return video_ids
        except KeyError as e:
            logger.error('cannot parse user info. reason:{}'.format(e))
            return video_ids

    def track(self):
        now = datetime.now()
        with Pool(30) as p:
            video_pages = p.map(VideoPage, self.new_videos)

        for video_page in video_pages:
            if video_page.is_finish == 1:
                t = Tempor(video_page.video_id, now,
                           video_page.views, video_page.likes,
                           video_page.dislikes, video_page.comments)
                db.insert(t, is_commit=False)
        db.conn.commit()


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
            'find cost {}; video number too small = {}, exit.'.format(time.time() - beg,
                                                                      len(job_instance.new_videos)))
        return
    else:
        print('find cost {}; there are {} video will be track.'.format(time.time() - beg,
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


atexit.register(at_exit)

job_instance = None
all_user = load_all_user()
index = int(sys.argv[1])
# index = 0
db = SqlXigua(index)
single_scheduler()
