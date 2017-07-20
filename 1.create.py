# -*- coding: utf-8 -*-
import sqlite3
import time


def timer():
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        return current_time


if __name__ == "__main__":
    conn = sqlite3.connect('wordpress.db')
    cursor = conn.cursor()
    check_table = "select * from sqlite_master where type='table' and name='library'"
    cursor.execute(check_table)
    result = cursor.fetchall()
    if not result:
        cursor.execute('''CREATE TABLE library
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    today DATETIME NOT NULL,
                    question VARCHAR(10) NOT NULL,
                    answer VARCHAR(10) NOT NULL,
                    author VARCHAR(100) NOT NULL,
                    title VARCHAR(100) NOT NULL,
                    agree INT NOT NULL,
                    record INT DEFAULT 0 NOT NULL,
                    post INT DEFAULT 0)''')
        conn.commit()
        print u"[{}] 创建数据表成功.".format(timer())
    else:
        print u"[{}] 数据表已经存在.".format(timer())
