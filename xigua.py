"""
xigua request module
"""
# coding: utf-8
import re
from datetime import datetime
import json
import requests
from utilities import record_data
from video import Video
from config import logging, XConfig


class VideoPage:
    """
    parse video page content
    """

    def __init__(self, video_id):
        self.video_id = video_id
        self.time = None
        self.views = -1
        self.likes = -1
        self.dislikes = -1
        self.comments = -1
        self.data = ''
        self.is_finish = False

        self.setup()

    def setup(self):
        """setup"""
        video_url = 'https://www.ixigua.com/a{}'.format(self.video_id)

        try:
            req = requests.get(video_url,
                               timeout=XConfig.TIMEOUT)
            self.data = req.text
            self.parse_views()
            self.parse_likes()
            self.parse_dislikes()
            self.parse_comments()
            self.is_finish = True
        except requests.HTTPError as http_e:
            logging.error('network error when request video page. Reason:{}'.format(http_e))
            self.is_finish = False
        except requests.Timeout:
            logging.error('time out when request video page. ')
            self.is_finish = False
        except AttributeError as attr_e:
            record_data(self.data)
            logging.error('attribution error occur. Reason:{}'.format(attr_e))
            self.is_finish = False

    def parse_views(self):
        """parse view count to self.views"""
        m = re.search("videoPlayCount: \d+", self.data)
        self.views = int(m.group(0)[16:])

    def parse_likes(self):
        """parse like count to self.likes"""
        raw_likes = re.search('diggCount: \d+', self.data).group(0)
        self.likes = int(raw_likes[11:])

    def parse_dislikes(self):
        """parse dislike count to self.dislikes"""
        raw_dislikes = re.search('buryCount: \d+', self.data).group(0)
        self.dislikes = int(raw_dislikes[11:])

    def parse_comments(self):
        """解析评论数据"""
        raw_comments = re.search('count: \d+', self.data).group(0)
        self.comments = int(raw_comments[7:])
