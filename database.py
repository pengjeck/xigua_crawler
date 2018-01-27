# coding: utf-8

from config import logging, XConfig
from sqlalchemy import Column, Integer, create_engine, TEXT, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Video(Base):
    __tablename__ = 'video'
    video_id = Column(TEXT, primary_key=True)
    user_id = Column(TEXT)
    title = Column(TEXT)
    upload_time = Column(DateTime)
    avatar_path = Column(TEXT)
    avatar_url = Column(TEXT)
    des = Column(TEXT)


class User(Base):
    __tablename__ = 'user'
    user_id = Column(TEXT, primary_key=True)
    followers = Column(Integer)
    watchers = Column(Integer)
    nickname = Column(TEXT)
    avatar_path = Column(TEXT)
    avatar_url = Column(TEXT)
    des = Column(TEXT)
    is_pro = Column(Integer)


class Tempor(Base):
    __tablename__ = 'tempor'
    id = Column(Integer, primary_key=True)
    video_id = Column(TEXT, nullable=True)
    time = Column(DateTime, nullable=True)
    views = Column(Integer)
    likes = Column(Integer)
    dislikes = Column(Integer)
    comments = Column(Integer)


def get_session(index):
    db_file = XConfig.INDEX_DB_FILE.format(index)
    _engine = create_engine('sqlite:///{}'.format(db_file))
    Base.metadata.create_all(_engine)
    db_session = sessionmaker(bind=_engine)
    return db_session()
