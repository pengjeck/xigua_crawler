# coding: utf-8

import subprocess
import time
import atexit

commands = [
    '/home/pj/datum/GraduationProject/pyenv/bin/python',
    '/home/pj/datum/GraduationProject/code/xigua_crawler/track.py',
    '1'
]

sub_ps = []


def at_exit():
    for process in sub_ps:
        process.kill()


atexit.register(at_exit)

for i in range(15):
    beg = time.time()
    commands[2] = str(i)
    sub_p = subprocess.Popen(commands)
    sub_ps.append(sub_p)
    print('{}th setup!'.format(i))
    time.sleep(900 - (time.time() - beg))

while True:
    print('all process is running.')
    q = input()
    if q == 'q':
        break

print('end')
