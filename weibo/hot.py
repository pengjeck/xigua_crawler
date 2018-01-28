# coding:utf-8

import re
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from sqlalchemy import Column, Integer, create_engine, TEXT, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class Instance:
    def __init__(self):
        engine = create_engine('sqlite:///weibo.db')
        self.ids = None
        self.titles = None
        db_session = sessionmaker(bind=engine)
        self.session = db_session()

    def update(self):
        date = datetime.utcnow()
        url = 'http://s.weibo.com/top/summary'
        params = {
            'Refer': 'top_hot',
            'topnav': 1,
            'mvr': 6
        }
        try:
            r = requests.get(url=url, params=params, timeout=10)
            raw = re.findall('list_realtimehot\\\\">[\d\w\\\. ]+<', r.text)
            titles = [title.encode('latin-1').decode('unicode_escape')[18:-1] for title in raw]
            for title in titles:
                self.session.add(Trend(title=title, date=date))
            self.session.commit()
        except (requests.Timeout, requests.HTTPError, requests.ConnectionError):
            pass


Base = declarative_base()


class Trend(Base):
    __tablename__ = 'trend'
    id = Column(Integer, primary_key=True)
    title = Column(TEXT(), nullable=True)
    date = Column(DateTime(), nullable=True)


def tick():
    instance.update()


if __name__ == '__main__':
    instance = Instance()
    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'interval', seconds=60)

    try:
        scheduler.start()
    except (SystemExit, KeyboardInterrupt):
        print('exit')
        scheduler.shutdown()
