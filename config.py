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
    USER_IDS_FILE = './data/user_ids.txt'
    VIDEO_AVATAR_PATH = './data/video_avatar/'
    USER_AVATAR_PATH = './data/user_avatar/'
    LOGGING_PATH = './data/log'
    INDEX_DB_FILE = './data/dbs/xigua{}.db'

    IS_TESTING = True

    TRACK_SPAN = 900  # 15 * 60 = 200 minute. 默认15分钟记录一次
    TIMEOUT = 3  # 3秒的超时时间

    BEFORE_TIMEDELTA = timedelta(minutes=10)  # 10分钟

    PROCESSES_NUM = 30  # pool(30)

    UA_DB_PATH = './data/1000-pc.log'

    @staticmethod
    def logging_file():
        """
        get logging file full path
        """
        return os.path.join(XConfig.LOGGING_PATH, '{}.txt'.format(int(time.time())))

    @staticmethod
    def get_proxy_bill_id():
        with open('./proxy/id.txt') as f:
            line = f.readline().strip()
        return line


logger = logging.getLogger('base')
formatter = logging.Formatter('%(asctime)s - %(message)s')

fh = logging.FileHandler(XConfig.logging_file())
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
