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
    DB_FILE = '/home/pj/datum/GraduationProject/dataset/xigua/xigua.db'
    VIDEO_AVATAR_PATH = '/home/pj/datum/GraduationProject/dataset/xigua/video_avatar/'
    USER_AVATAR_PATH = '/home/pj/datum/GraduationProject/dataset/xigua/user_avatar/'
    LOGGING_PATH = '/home/pj/datum/GraduationProject/dataset/xigua/log'

    IS_TESTING = False

    TRACK_SPAN = 900  # 15 * 60 = 200 minute. 默认15分钟记录一次
    TIMEOUT = 3  # 3秒的超时时间

    BEFORE_TIMEDELTA = timedelta(minutes=10)  # 10分钟

    PROCESSES_NUM = 30  # pool(30)

    @staticmethod
    def logging_file():
        """
        get logging file full path
        """
        return os.path.join(XConfig.LOGGING_PATH, '{}.txt'.format(int(time.time())))


# logging.basicConfig(level=logging.INFO,
#                     handlers=[logging.FileHandler(XConfig.logging_file()),
#                               logging.StreamHandler()])

logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(XConfig.logging_file())])
