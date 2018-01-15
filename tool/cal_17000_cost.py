# coding: utf-8

f = open('clipboard.txt')
total_cost = 0
while True:
    line = f.readline()
    if len(line) < 1:
        break
    onetime = float(line.split(' ')[2])
    total_cost += onetime
print(total_cost)
f.close()
