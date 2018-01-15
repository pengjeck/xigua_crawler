# coding: 'utf-8'

with open('clipboard.txt', 'r') as read_f, open('out.txt', 'w') as write_f:
    read_line = read_f.readline()
    while len(read_line) != 0:
        parts = [part.strip() for part in read_line.split(':')]
        write_line = "'" + parts[0] + "':'" + parts[1] + "',\n"
        write_f.write(write_line)
        read_line = read_f.readline()

