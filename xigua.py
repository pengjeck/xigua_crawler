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


def avatar_url_parse(item):
    """
    :param item: json object
    :param avatar_type: select from in (video, user)
    """
    # TODO: finish avatar url parse
    pass


class SearchPage:
    """
    处理请求YouTube搜索页面的返回数据
    """

    def __init__(self, query_string):
        self.query_string = query_string
        self._max_results = YConfig.SEARCH_PAGE_SIZE
        self._after_delta = YConfig.BEFORE_TIMEDELTA
        self.data = None
        self.vid_ids = []
        self.vids = []

        self.search()
        if self.data is not None:
            self.parse_video()  # 简单的解析视频

    def search(self):
        """
        search video
        """
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'part': 'snippet',
            'q': self.query_string,
            'type': 'video',
            'maxResults': self._max_results,
            'key': YConfig.KEYS[0],
            'publishedAfter': time_rfc3339(self._after_delta)
        }
        try:
            req = requests.get(search_url, params=params,
                               proxies=YConfig.PROXIES,
                               timeout=YConfig.TIMEOUT)
            self.data = json.loads(req.text)
            # 数据不对
            if self.data['kind'] != 'youtube#searchListResponse':
                self.data = None
        except requests.HTTPError as http_e:
            logging.error('network error when request search. msg:{}'.format(http_e))
        except requests.Timeout:
            logging.error('timeout when request search')

    def parse_video(self):
        """
        解析search中video数据
        """
        for item in self.data['items']:
            if item['id']['kind'] != 'youtube#video':
                continue
            try:
                vid_id = item['id']['videoId']
                vid = Video(vid_id)
                vid.avatar_url = avatar_url_parse(item, 'video')
                vid.des = item['snippet']['description']
                vid.title = item['snippet']['title']
                vid.upload_time = youtube_timedecoder(
                    item['snippet']['publishedAt'])
                self.vids.append(vid)
                self.vid_ids.append(vid_id)
            except TypeError as type_e:
                record_data(item, 'parse_video.json')
                logging.error("[{}] error occur when parsing video, msg:{}".format(datetime.now(), type_e))
            except KeyError as key_e:
                record_data(item, 'parse_video.json')
                logging.error("[{}] error occur when parsing video, msg:{}".format(datetime.now(), key_e))


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
        video_url = 'https://www.youtube.com/watch'
        params = {
            'v': self.video_id
        }
        try:
            req = requests.get(video_url, params=params,
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
        row_views = re.search('"view_count":"\d+"', self.data).group(0)[14:-1]
        self.views = int(row_views)

    def parse_likes(self):
        """parse like count to self.likes"""
        row_likes = re.search(
            'like this video along with [\d,]+ other people', self.data).group(0)
        self.likes = int(re.search('\d+', row_likes.replace(',', '')).group(0))

    def parse_dislikes(self):
        """parse dislike count to self.dislikes"""
        row_likes = re.search(
            'dislike this video along with [\d,]+ other people', self.data).group(0)
        self.dislikes = int(re.search('\d+', row_likes.replace(',', '')).group(0))

    def parse_comments(self):
        """
        do not finish this method
        """
        self.comments = -1


class UserPage:
    def __init__(self, user_id):
        pass

    def setup(self):
        pass

    def user(self, user_id):
        """
        get user's informat
        :param user_id: user's id
        """
        user_url = 'https://www.youtube.com/channel/{}'.format(user_id)
        data = requests.get(user_url, proxies=YConfig.PROXIES)
        return data
