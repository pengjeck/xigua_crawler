# coding: utf-8

import subprocess
import time
import atexit

commands = [
    '/home/pj/datum/GraduationProject/pyenv/bin/python ',
    '/home/pj/datum/GraduationProject/code/xigua_crawler/track.py'
]

sub_ps = []


def at_exit():
    for process in sub_ps:
        process.kill()


atexit.register(at_exit)
for i in range(1000):
    beg = time.time()
    sub_p = subprocess.Popen(commands)
    sub_ps.append(sub_p)
    print('{}th setup!'.format(i))
    time.sleep(400 - (time.time() - beg))

while True:
    q = input()
    if q == 'q':
        break

print('end')
