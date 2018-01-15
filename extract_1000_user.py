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
import sqlite3
import json
from config import logging
import time
from user import User
from multiprocessing import Pool

IS_DEBUGGING = True  # 是否正在调试


class ExtractDatabase:
    def __init__(self):
        self._total_db_file = '/home/pj/datum/GraduationProject/dataset/xigua/xigua.db'
        self.all_connection = sqlite3.connect(self._total_db_file)
        self.all_cur = self.all_connection.cursor()

        self._new_db = '/home/pj/datum/GraduationProject/dataset/xigua/extract_user.db'
        self.new_connection = sqlite3.connect(self._new_db)
        self.new_cur = self.new_connection.cursor()

    def update_followers(self, user_id, followers):
        """
        更新total_database中一个用户的粉丝数目
        :param user_id:
        :param followers:
        :return:
        """
        try:
            sql = """update user set followers=? where user_id=?"""
            self.all_cur.execute(sql, (followers, user_id))
            return True
        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
            logging.error('cannot update {} followers to {}'.format(user_id, followers))
            return False

    def update_users(self, user_obj):
        """
        更新用户信息
        :param user_obj:
        :return:
        """
        if not isinstance(user_obj, User):
            raise TypeError('parameter must satisfy type(user_obj) == User')
        try:
            sql = """update user set 
                followers=?,
                watchers=?,
                nickname=?,
                avatar_path=?,
                avatar_url=?,
                des=?,
                is_pro=? where user_id=?"""
            self.all_cur.execute(sql, (user_obj.followers, user_obj.watchers,
                                       user_obj.nickname, user_obj.avatar_path,
                                       user_obj.avatar_url, user_obj.des,
                                       user_obj.is_pro, user_obj.user_id))
            return True
        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
            logging.error('cannot update user_id={} user info'.format(user_obj.user_id))
            return False

    def get_all_users(self):
        """
        从数据库中抽取所有用户
        :return:
        """
        try:
            sql = """select user_id from user"""
            res = self.all_cur.execute(sql)
            return res
        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
            logging.error('cannot get all user_id from total_bd')
            return None

    def insert(self, user_obj):
        """
        将采样之后的数据放到新的数据库中。
        :param user_obj: 用户对象
        :return:
        """
        try:
            sql = """insert into user values(?,?,?,?,?,?,?);"""
            self.new_cur.execute(sql, user_obj.dump())
            return True
        except (sqlite3.ProgrammingError, sqlite3.OperationalError):
            logging.error('cannot insert new user into user ')

    def __del__(self):
        self.all_connection.close()
        self.new_connection.close()


class ConfigInfo:
    def __init__(self):
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
        self.cookies = {
            'csrftoken': 'f07abcdea7036c89aa516b67c44cbf0b',  # 一年
            'tt_webid': '6510022945200047630',  # 10年
            '_ga': 'GA1.2.1807487632.1515732834',  # 两年
            '_gid': 'GA1.2.2105862598.1515732834',  # 一天
            '_ba': 'BA0.2-20171227-51225-0QOfevbdMYurWcR3FEl'  # 两年
        }
        self.timeout = 3


class Extract:
    """
    抽取1000个用于跟踪的用户
    """

    def __init__(self):
        self._base_user_url = 'https://m.ixigua.com/video/app/user/home/'
        self.config = ConfigInfo()

    def sampling(self):
        """采样（分层采样）
        # TODO: 采样算法实现
        """
        pass

    def get_users_url(self, user_ids):
        """
        从user_id中提取用户页面的url
        :param user_ids: 用户id
        :return:
        """
        if not isinstance(user_ids, (list, tuple)):
            logging.error('user_ids must be list or tuple in func=get_user_url')
        user_urls = []
        pre_params = {
            'to_user_id': '',
            'format': 'json'
        }
        for user_id in user_ids:
            pre_params['to_user_id'] = user_id
            user_urls.append(Extract._url_join(self._base_user_url, pre_params))
        return user_urls

    def get_user_url(self, user_id):
        """
        :return:
        """
        params = {
            'to_user_id': user_id,
            'format': 'json'
        }
        return Extract._url_join(self._base_user_url, params)

    @staticmethod
    def _url_join(base_url, params):
        """
        连接url和params
        :param base_url:
        :param params:
        :return:
        """
        if not isinstance(params, dict):
            logging.error('url params must be dictionary')
        if base_url[-1] != '?':
            base_url += '?'
        for keys in params:
            item = "{}={}&".format(keys, params[keys])
            base_url += item
        return base_url[:-1]

    def parse_user_page(self, user_id):
        """
        解析用户页面
        :param user_id:
        :return: User对象
        """
        url = self.get_user_url(user_id)
        try:
            req = requests.get(url, cookies=self.config.cookies,
                               headers=self.config.headers,
                               timeout=self.config.timeout)
            data = json.loads(req.text.encode('utf-8'), encoding='ascii')
            if data['message'] != 'success':
                logging.info('do not success when request user page!')
                return None

            user = User(user_id)
            user.followers = int(data['user_info']['followers_count'])
            user.watchers = int(data['user_info']['following_count'])
            user.des = data['user_info']['description']
            user.avatar_url = data['user_info']['avatar_url']
            user.nickname = data['user_info']['name']
            if data['user_info']['user_verified'] == 'true':
                user.is_pro = 1
            else:
                user.is_pro = False
            return user
        except (requests.Timeout, requests.HTTPError, requests.ConnectionError):
            logging.error('failed to request user page = {}'.format(url))
            return None
        except json.JSONDecodeError:
            logging.error('cannot decode {} response data to json object'.format(url))
            return None
        except KeyError as e:
            logging.error('cannot parse user info. reason:{}'.format(e))
            return None


db_instance = ExtractDatabase()
ex = Extract()

all_users = db_instance.get_all_users()
all_users = [user[0] for user in all_users]  # 0.007秒,应该算很快的吧


pool_size = 30

for i in range(int(len(all_users) / 30)):
    try:
        beg = time.time()
        with Pool(pool_size) as p:
            users = p.map(ex.parse_user_page, all_users[i * 30: (i + 1) * 30])
        for user in users:
            if not isinstance(user, User):
                continue
            db_instance.update_users(user)
        db_instance.all_connection.commit()
        print("{}th cost {}".format(i, time.time() - beg))
    except:
        pass
# TODO:没有做
