# coding: utf-8
import time
from apscheduler.schedulers.blocking import BlockingScheduler


def time_consume():
    time.sleep(5)


b = BlockingScheduler()
b.add_job(time_consume, 'interval', seconds=10)
b.start()