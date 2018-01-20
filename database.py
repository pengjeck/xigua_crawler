# coding: utf-8

import sqlite3
import os
from user import User
from video import Video
from tempor import Tempor
from config import logging, XConfig


class SqlXigua:
    """database interface"""

    def __init__(self):
        self.conn = sqlite3.connect(XConfig.DB_FILE)
        self.cur = self.conn.cursor()
        if XConfig.IS_TESTING:
            # 清除表中所有的数据
            self.cur.execute('delete from tempor')
            self.conn.commit()

    def create_tables(self):
        self.cur.execute("CREATE TABLE video (video_id TEXT PRIMARY KEY,\
                                              user_id TEXT,\
                                              title TEXT,\
                                              upload_time timestamp,\
                                              avatar_path TEXT,\
                                              avatar_url TEXT, \
                                              des TEXT)")
        self.cur.execute("CREATE TABLE user (user_id TEXT PRIMARY KEY,\
                                             followers INTEGER,\
                                             watchers INTEGER,\
                                             nickname TEXT,\
                                             avatar_path TEXT,\
                                             avatar_url TEXT,\
                                             des TEXT,\
                                             is_pro INTEGER)")
        self.cur.execute("CREATE TABLE tempor (video_id TEXT,\
                                               time timestamp,\
                                               views INTEGER,\
                                               likes INTEGER,\
                                               dislikes INTEGER,\
                                               comments INTEGER)")

    def execute_sql(self, sql_lan):
        """
        execute other sql words
        """
        try:
            self.cur.execute(sql_lan)
            self.conn.commit()
        except sqlite3.OperationalError as o_e:
            logging.exception(o_e)

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
            self.cur.execute(sql, (user_obj.followers, user_obj.watchers,
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
            res = self.conn.execute(sql)
            return res
        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
            logging.error('cannot get all user_id from total_bd')
            return None

    def insert(self, obj, is_commit=True):
        """
        insert a object to database.
        """
        if isinstance(obj, Video):
            self._insert_video(obj, is_commit)
        elif isinstance(obj, User):
            self._insert_user(obj, is_commit)
        elif isinstance(obj, Tempor):
            self._insert_tempor(obj, is_commit)
        else:
            raise TypeError('insert should be Video, User, Tempor')

    def _insert_user(self, user_obj, is_commit):
        if not isinstance(user_obj, User):
            raise TypeError('expect User object')
        self.cur.execute("INSERT INTO user VALUES(?,?,?,?,?,?,?,?)", user_obj.dump())
        if is_commit:
            self.conn.commit()

    def _insert_video(self, video_obj, is_commit):
        if not isinstance(video_obj, Video):
            raise TypeError('expect Video object')
        self.cur.execute("INSERT INTO video VALUES(?,?,?,?,?,?,?)",
                         video_obj.dump())
        if is_commit:
            self.conn.commit()

    def _insert_tempor(self, tempor_obj, is_commit):
        if not isinstance(tempor_obj, Tempor):
            raise TypeError('expect tempor object')
        self.cur.execute("INSERT INTO tempor VALUES(?,?,?,?,?,?)",
                         tempor_obj.dump())
        if is_commit:
            self.conn.commit()

    def __del__(self):
        self.conn.close()
