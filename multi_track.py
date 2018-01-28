# coding: utf-8

import subprocess
import time
import atexit
import sys
import os

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

end_index = int(sys.argv[1])
count = 0
while True:
    beg = time.time()
    commands[2] = str(count)
    sub_p = subprocess.Popen(commands)
    print('{}th setup!'.format(count))
    time.sleep(600 - (time.time() - beg))
    # 上面一个程序肯定已经退出了
    pid_path = 'data/pids/{}'.format(sub_p.pid)
    if os.path.isfile(pid_path):
        sub_ps.append(sub_p)
        count += 1
        if count == end_index:
            break


while True:
    print('all process is running.')
    q = input()
    if q == 'q':
        break

print('end')
