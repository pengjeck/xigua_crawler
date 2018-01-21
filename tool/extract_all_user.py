# coding: utf-8

import sqlite3

USER_IDS_FILE = '/home/pj/datum/GraduationProject/dataset/xigua/user_ids.txt'
DB_FILE = '/home/pj/datum/GraduationProject/dataset/xigua/xigua.db'


def extract_to_file():
    conn = sqlite3.connect(DB_FILE)

    sql = """select user_id from user"""
    res = conn.execute(sql)
    user_ids = [user[0] for user in res]
    with open('user_ids.txt', 'w') as f:
        f.writelines('\n'.join(user_ids))

    conn.close()


def read_user():
    with open(USER_IDS_FILE, 'r') as f:
        return f.readlines()


# extract_to_file()
print(len(read_user()))