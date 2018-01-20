# coding: utf-8

import subprocess
import atexit

commands = [
    'python',
    'time_consume.py'
]

pids = []


def fun():
    for p in pids:
        p.kill()


atexit.register(fun)

for i in range(1000):
    p = subprocess.Popen(commands)
    pids.append(p)
print('stop')
a = input()
