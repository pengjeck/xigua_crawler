"""
xigua request module
"""
# coding: utf-8
import re
import requests
from config import logging, XConfig
import random


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

        self.ua = VideoPage.get_ua()
        """
        1 没有错误
        2 网络错误
        3 请求错误，应该是被网站拦截了
        4 其他错误
        """
        self.status = 1

        self.setup()

    @staticmethod
    def get_ua():
        ua_index = random.randint(0, 300)
        f = open(XConfig.UA_DB_PATH, 'r')
        # 这个过程可能会比较耗时
        for _ in range(ua_index):
            f.readline()
        return f.readline().strip()

    def setup(self):
        """setup"""
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,pt;q=0.8,zh-CN;q=0.7,zh;q=0.6',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': self.ua
        }

        video_url = 'https://www.ixigua.com/a{}'.format(self.video_id)

        try:
            req = requests.get(url=video_url,
                               headers=headers,
                               timeout=XConfig.TIMEOUT)
            if req.status_code == 404:
                self.status = 4
                return

            self.data = req.text
            self.parse_views()
            self.parse_likes()
            self.parse_dislikes()
            self.parse_comments()
            self.status = 1  # 没有错误
        except requests.HTTPError as http_e:
            logging.error('network error when request video page. Reason:{}'.format(http_e))
            self.status = 2
        except requests.Timeout:
            logging.error('time out when request video page. ')
            self.status = 3
        except AttributeError as attr_e:
            # record_data(self.data, type='html')
            if len(self.data) < 200:
                # 换一个ua再来一次
                self.ua = self.get_ua()
                self.setup()
                if self.status != 1:
                    logging.error('block by the website. request content : {}'.format(self.data))
                    self.status = 3
            else:
                logging.error('attribution error occur. Reason:{}'.format(attr_e))
                self.status = 4

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
