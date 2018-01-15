# coding: ** utf-8 **

import requests
import json
import time
import os
import datetime
import logging
from .save import save_json_to_file

logging.basicConfig(filename='download.log', level=logging.DEBUG)

query_str = {
    'min_behot_time': '0',
    'category': 'video_new',
    'utm_source': 'toutiao',
    'widen': '1',
    'tadrequire': 'false',
    'as': 'A1652A14D350E8A',
    'cp': '5A43706EE82A5E1'
}

base_url = 'https://www.ixigua.com/api/pc/feed/'


def get_video_feeds(times, time_span=30):
    """
    批量获取一段时间内的热点视频数据
    :return:
    """
    for i in range(times):
        min_behot_time = get_now_min_behot_time()
        save_video_feed(min_behot_time)
        time.sleep(time_span)


def save_video_feed(min_behot_time):
    """
    获取视频相关信息
    :param min_behot_time:
    :return:
    """
    try:
        query_str['min_behot_time'] = min_behot_time
        r = requests.get(url=base_url, params=query_str)
        data = json.loads(r.text, encoding=r.apparent_encoding)
        file = save_json_to_file(data, str(min_behot_time))
        logging.info("{} save!!!".format(file))
        return file
    except requests.RequestException:
        logging.exception("network error!!cannot get behot={} video feed".format(min_behot_time))
        return None


def get_now_min_behot_time():
    return int(time.time())


def get_video_url(group_ids):
    """
    获取视频的网页播放url
    :param group_ids:
    :return:
    """
    ori_url = 'https://www.ixigua.com/'
    if isinstance(group_ids, list):
        return [ori_url + 'a' + group_id for group_id in group_ids]
    elif isinstance(group_ids, str):
        return ori_url + 'a' + group_ids


def parse_download_url(url=None):
    """
    点量视频解析服务，15s解析一次
    :param url:
    :return:
    """
    parse_server_url = 'http://api.v2.flvurl.cn/parse/'
    params = {
        'appid': '6170b6db0a881c18389f47d6d994340e',
        'type': 'vod',
        'url': url
    }
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'api.v2.flvurl.cn',
        'Origin': 'http',
        'Referer': 'http',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
    }
    try:
        resp = requests.get(parse_server_url, params=params, headers=headers)
        data = json.loads(resp.text, encoding=resp.apparent_encoding)
        save_json_to_file(data, filename='out', directory='tmp')
        return data['data']['streams'][0]['segs'][0]['url']
    except Exception as e:
        logging.exception("failed to parse {}'s download url, may because {}".format(url, e))
        # print("failed to parse {}'s download url, may because {}".format(url, e))
        return None


def download_video(video_url, filename, path):
    """
    下载视频
    :param video_url:视频
    :param filename: 文件名
    :param path:路径
    :return:
    """
    try:
        r = requests.get(video_url, stream=True)
        with open('{}/{}.mp4'.format(path, filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        logging.exception("failed to download video {} may because {}".format(video_url, e))
        # print("failed to download video {} may because {}".format(video_url, e))
        return False


def batch_download():
    """
    开始大批量的下载视频。
    :return:
    """
    ori_path = '/home/pj/pro/python/video_recommendation/try/xigua/data'
    filenames = os.listdir(ori_path)
    files = [os.path.join(ori_path, filename) for filename in filenames]
    target_path = '/home/pj/pro/python/video_recommendation/try/xigua/video'
    for file in files:
        with open(file, 'r') as f:
            json_obj = json.load(f)
            beg_time = datetime.datetime.now()
            for (index, video_info) in enumerate(json_obj['data']):
                video_url = get_video_url(video_info['group_id'])
                download_url = parse_download_url(video_url)
                if download_url is not None:
                    json_obj['data'][index]['download_url'] = download_url
                    logging.info('downloading {} in {}'.format(video_info['group_id'], file))
                    print('downloading {} in {}'.format(video_info['group_id'], file))
                    download_video(download_url, video_info['group_id'], target_path)
                    logging.info('downloaded {} in {}'.format(video_info['group_id'], file))
                    print('downloaded {} in {}'.format(video_info['group_id'], file))
                mid_time = datetime.datetime.now()
                if (mid_time - beg_time).total_seconds() > 15:
                    beg_time = datetime.datetime.now()
                else:
                    time.sleep(16 - (mid_time - beg_time).total_seconds())
