"""
config module
"""
# coding: utf-8

import logging
import time
import os
from datetime import timedelta


class XConfig:
    """
    youtube crawler config file
    """
    USER_IDS_FILE = '/home/pj/datum/GraduationProject/dataset/xigua/user_ids.txt'
    VIDEO_AVATAR_PATH = '/home/pj/datum/GraduationProject/dataset/xigua/video_avatar/'
    USER_AVATAR_PATH = '/home/pj/datum/GraduationProject/dataset/xigua/user_avatar/'
    LOGGING_PATH = '/home/pj/datum/GraduationProject/dataset/xigua/log'
    INDEX_DB_FILE = '/home/pj/datum/GraduationProject/dataset/xigua/database/xigua{}.db'
    DB_FILE = '/home/pj/datum/GraduationProject/dataset/xigua/xigua.db'

    IS_TESTING = True

    TRACK_SPAN = 900  # 15 * 60 = 200 minute. 默认15分钟记录一次
    TIMEOUT = 3  # 3秒的超时时间

    BEFORE_TIMEDELTA = timedelta(minutes=10)  # 10分钟

    PROCESSES_NUM = 30  # pool(30)

    HEADERS_1 = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Mobile Safari/537.36',
    }

    HEADERS_2 = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }

    HEADERS_3 = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'm.365yg.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Mobile Safari/537.36',
    }

    HEADERS_4 = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'm.365yg.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }

    COOKIES = {
        'csrftoken': 'f07abcdea7036c89aa516b67c44cbf0b',  # 一年
        'tt_webid': '6510022945200047630',  # 10年
        '_ga': 'GA1.2.1807487632.1515732834',  # 两年
        '_gid': 'GA1.2.2105862598.1515732834',  # 一天
        '_ba': 'BA0.2-20171227-51225-0QOfevbdMYurWcR3FEl'  # 两年
    }

    @staticmethod
    def logging_file():
        """
        get logging file full path
        """
        return os.path.join(XConfig.LOGGING_PATH, '{}.txt'.format(int(time.time())))


logger = logging.getLogger('base')
formatter = logging.Formatter('%(asctime)s - %(message)s')

fh = logging.FileHandler(XConfig.logging_file())
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
