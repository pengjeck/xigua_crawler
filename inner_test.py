# coding: utf-8
import requests
import re

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'm.ixigua.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Mobile Safari/537.36',
}

cookies = {
    'csrftoken': 'f07abcdea7036c89aa516b67c44cbf0b',  # 一年
    'tt_webid': '6510022945200047630',  # 10年
    '_ga': 'GA1.2.1807487632.1515732834',  # 两年
    '_gid': 'GA1.2.2105862598.1515732834',  # 一天
    '_ba': 'BA0.2-20171227-51225-0QOfevbdMYurWcR3FEl'  # 两年
}


def get_video_type():
    return ['subv_voice', 'subv_funny', 'subv_society',
            'subv_comedy', 'subv_life', 'subv_movie',
            'subv_entertainment', 'subv_cute', 'subv_game',
            'subv_boutique', 'subv_broaden_view', 'video_new']


def test_be_hot_data():
    params = {
        'tag': 'video_new',
        'ac': 'wap',
        'count': '20',
        'format': 'json_raw',
        'as': 'A135CAC5F8B2CC3',
        'cp': '5A58220C8CD32E1',
        'max_behot_time': '1515727802'
    }

    base_url = 'http://m.ixigua.com/list/'

    r = requests.get(base_url,
                     params=params,
                     headers=headers,
                     cookies=cookies)

    print(r.apparent_encoding)  # 这个操作可能是非常耗时的，如果可以的话，记录一次下次就直接替换掉


def test_user_page(page_type='m'):
    """
    测试用户页面的请求情况和数据
    :param page_type: 如果是m表示是移动网页，如果是pc则表示是电脑版网页端。目前只支持移动端的网页
    :return:
    """
    if page_type != 'm':
        raise TypeError('this method only support mobile version')

    params = {
        'to_user_id': '5567057918',
        'format': 'html'
    }
    base_url = 'https://m.ixigua.com/video/app/user/home/'

    req = requests.get(base_url, params=params, cookies=cookies, headers=headers)

    # 其实测试代码可以不用写得那么完整
    res = req.text.find('user-vip')
    if res == -1:
        print('this user is not pro!')
    else:
        print('this user is pro')

    pos = req.text.find('人关注')
    followers = re.search('\d+$', req.text[pos - 15:pos]).group(0)
    print(followers)

    

test_user_page()
