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
import random
import requests
from itertools import product
import json
from config import logger, XConfig
from multiprocessing import Pool
from database import Tempor, get_session
from xigua import VideoPage
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
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0'
        }
        # self.new_videos = list(session.query(Tempor.video_id).distinct())
        self.get_new_videos()

    @staticmethod
    def test_ua_valid(ua):
        """
        测试ua的有效性
        :param ua: user-agent
        :return:
        """
        base_user_url = 'https://m.ixigua.com/video/app/user/home/?to_user_id=3844228581&format=json'
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
            'upgrade-insecure-requests': '1',
            'user-agent': ua
        }
        try:
            req = requests.get(url=base_user_url,
                               timeout=XConfig.TIMEOUT, headers=headers)
            if req.status_code == 403:
                return False
            else:
                return True
        except (requests.HTTPError, requests.ConnectionError,
                requests.Timeout):
            return True

    def _change_headers(self, times=15):
        for _ in range(times):
            # 太多太耗时了
            ua_index = random.randint(0, 200)
            f = open(XConfig.UA_DB_PATH, 'r')
            # 这个过程可能会比较耗时
            for _ in range(ua_index):
                f.readline()
            ua = f.readline().strip()
            if Instance.test_ua_valid(ua):
                self.headers['user-agent'] = ua
                return True
        return False

    def get_new_videos(self):
        """
        获取最新的视频（全量搜索）'
        :return:
        """
        for i in range(int(len(all_user) / self._pool_size)):
            # beg = time.time()
            with Pool(self._pool_size) as p:
                part_users = all_user[i * self._pool_size: (i + 1) * self._pool_size]
                results = p.map(self._get_new_video, part_users)

            is_need_change_ua = False
            for res in results:
                if res['code'] == 200:
                    self.new_videos.extend(res['video_ids'])
                if res['code'] == 403:
                    is_need_change_ua = True

            # print('{} cost {}'.format(i, time.time() - beg))
            if is_need_change_ua:
                self._change_headers()

        self.new_videos = list(set(self.new_videos))

        for video_id in self.new_videos:
            t = Tempor(video_id=video_id, time=datetime.now(),
                       views=0, likes=0, dislikes=0,
                       comments=0)
            session.add(t)
        session.commit()

    def _get_new_video(self, user_id):
        """
        解析用户页面
        :param user_id:
        :return: User对象
        """
        base_user_url = 'https://m.ixigua.com/video/app/user/home/'
        params = {
            'to_user_id': user_id,
            'format': 'json',
        }
        res = {
            'code': 300,
            'video_ids': []
        }
        try:
            req = requests.get(base_user_url,
                               params=params,
                               headers=self.headers,
                               timeout=XConfig.TIMEOUT)

            if req.status_code == 403:
                logger.info('403 occur!!!')
                res['code'] = 403
                return res

            data = json.loads(req.text.encode('utf-8'), encoding='ascii')
            if data['message'] != 'success':
                logger.info('do not success when request user page!')
                res['code'] = 502
                return res

            now = time.time()
            for item_v in data['data']:
                try:
                    if now - int(item_v['publish_time']) < 360:
                        video_id = item_v['group_id_str']
                        res['video_ids'].append(video_id)
                except KeyError as e:
                    logger.error('cannot parse video_id. reason:{}'.format(e))
                    pass

            res['code'] = 200
            return res
        except requests.Timeout:
            logger.error('time out request user page')
            return res
        except requests.ConnectionError:
            logger.error('connection error occur when request user ')
            return res
        except requests.HTTPError:
            logger.error('http error when request user page')
            return res
        except json.JSONDecodeError as e:
            logger.error('cannot decode response data to json object {}'.format(e))
            return res
        except KeyError as e:
            logger.error('cannot parse user info. reason:{}'.format(e))
            return res

    def track(self):
        now = datetime.now()
        with Pool(30) as p:
            video_pages = p.map(VideoPage, self.new_videos)

        for video_page in video_pages:
            if video_page.status == 1:
                t = Tempor(video_id=video_page.video_id, time=now,
                           views=video_page.views, likes=video_page.likes,
                           dislikes=video_page.dislikes, comments=video_page.comments)
                session.add(t)
        session.commit()


def tick():
    job_instance.track()


def single_scheduler():
    global job_instance
    global all_user
    beg = time.time()
    job_instance = Instance()
    del all_user
    if len(job_instance.new_videos) < 1:
        print(
            'find cost {}; video number too small = {}, exit.'.format(time.time() - beg,
                                                                      len(job_instance.new_videos)))
        return
    else:
        print('find cost {}; there are {} video will be track.'.format(time.time() - beg,
                                                                       len(job_instance.new_videos)))
        scheduler = BlockingScheduler()
        # scheduler.add_executor('processpool')
        # scheduler.add_job(tick, 'interval', seconds=XConfig.TRACK_SPAN)
        scheduler.add_job(tick, 'interval', seconds=300)
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
    global session
    print('process exited!!')
    session.close()


atexit.register(at_exit)

job_instance = None
all_user = load_all_user()
index = int(sys.argv[1])
# index = 0
session = get_session(index)
single_scheduler()
