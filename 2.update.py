# -*- coding: UTF-8 -*-
# 用于时时更新首页内容
import re
import time
import sqlite3
import requests
from lxml import etree


def write_log(content):
    with open('log.txt', 'a') as f:
        f.writelines(content)


def timer():
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        return current_time


def download():
    url = 'http://duzhihu.cc/'
    headers = {
               'Host': 'duzhihu.cc',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'
               }
    html = requests.get(url, headers=headers).text
    selector = etree.HTML(html)
    content = selector.xpath('//div[@class="answer_item"]')
    p_question = re.compile('/question/(\d+)/')
    p_answer = re.compile('/answer/(\d+)')
    result = []
    for a in content:
        link = a.xpath('.//div[2]/a/@href')[0]  # 答案地址
        question = p_question.findall(link)[0]  # 问题ID
        answer = p_answer.findall(link)[0]  # 答案ID

        title = a.xpath('.//h3/a/text()')[0]
        author = a.xpath('.//div/div[2]/p/text()')[0]
        agree = a.xpath('.//div/div[3]/span/text()')[0]
        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        result.append((today, question, answer, author, title, agree))
    
    return result


class DataDB(object):
    def __init__(self):
        self.conn = sqlite3.connect('wordpress.db')
        self.cursor = self.conn.cursor()
        content = u"[{}] 连接数据库成功.".format(timer())
        print content
        write_log([content.encode('utf8'), '\n'])
        self.today = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    def insert(self, data):
        try:
            self.cursor.execute("SELECT * FROM library WHERE answer = ?", (data[2],))  # 该回答是否入库
            ret = self.cursor.fetchone()
            if ret:  # 已经存在该回答
                if ret[1] != self.today:  # 并且不是今天还没检测到过
                    self.cursor.execute("UPDATE library SET today=?, agree=?, record=?, post=? WHERE id=?", (self.today, ret[6], ret[7]+1, 0, ret[0],))  # 更新赞数以及日期，并且将重复记录加1
                    self.conn.commit()
                    content = u"[{}] 更新记录成功.".format(timer())
                    print content
                    return 1
                else:
                    print u"[{}] 跳过已存在记录.".format(timer())
                    return 2
            else:
                self.cursor.execute("INSERT INTO library (today,question,answer,author,title,agree) VALUES (?, ?, ?, ?, ?, ?)", data)
                print u"[{}] 插入记录成功.".format(timer())
                self.conn.commit()
                return 0
        except Exception as error:
            print error
            write_log([error, '\n'])
            return -1

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        content = "[{}] 程序结束运行.".format(timer())
        print content
    

if __name__ == "__main__":
    insert_count = 0
    update_count = 0
    pass_count = 0
    error_count = 0
    zhihu = download()  # 同步网络数据
    db = DataDB()
    for d in zhihu:
        status = db.insert(d)
        if status == 0:
            insert_count += 1
        elif status == 1:
            update_count += 1
        elif status == 2:
            pass_count += 1
        else:
            error_count += 1
    del db
    content = u'[{}] 更新{}条，跳过{}条，插入{}条，出错{}次.'.format(timer(), update_count, pass_count, insert_count, error_count)
    print content
    write_log([content.encode('utf8'), '\n'])
