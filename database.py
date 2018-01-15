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
        if XConfig.IS_TESTING and os.path.isfile(XConfig.DB_FILE):
            os.remove(XConfig.DB_FILE)
        self.conn = sqlite3.connect(XConfig.DB_FILE)
        self.cur = self.conn.cursor()
        if XConfig.IS_TESTING:
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
