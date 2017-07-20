# -*- coding: UTF-8 -*-
import re
import time
import sqlite3
import requests
from lxml import etree
import datetime
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc import WordPressPost


def write_log(content):
    with open('log.txt', 'a') as f:
        f.writelines(content)


def timer():
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        return current_time


class WordPress(object):
    def __init__(self):
        self.conn = sqlite3.connect('wordpress.db')
        self.cursor = self.conn.cursor()
        content = u"[{}] 启动自动发布程序.".format(timer())
        print content
        write_log([content.encode('utf8'), '\n'])
        self.today = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    def submit(self, content):
        client = Client('http://域名或ip/xmlrpc.php', '用户名', '密码')
        post = WordPressPost()
        # 设置标题
        title = '{} - 今日更新'.format(self.today)
        post.title = title
        post.content = content
        post.date = datetime.datetime.now() - datetime.timedelta(hours=8)
        # 添加标签设置分类目录
        post.terms_names = {
                        'post_tag': ['知乎', '每日更新'],
                        'category': ['知乎']
        }
        post.id = client.call(posts.NewPost(post))
        post.post_status = 'publish'
        status = client.call(posts.EditPost(post.id, post))
        return status

    def rules(self):
        try:  # 历史未曾出现过的答案，并且今天还没有更新过
            self.cursor.execute("SELECT * FROM library WHERE today=? and record=0 and agree>500 and agree<1500 and post=0 ORDER BY agree DESC", (self.today,))
            ret = self.cursor.fetchall()
            new_answer = ''
            new_count = len(ret)
            if ret:
                for r in ret:
                    link = "https://www.zhihu.com/question/{}/answer/{}".format(r[2], r[3])
                    new_answer += '[%s][%s]<a href="%s" target="_blank">%s</a>\n' % (r[6], r[4], link, r[5])

                    self.cursor.execute("UPDATE library SET post=? WHERE id=?", (r[8] + 1, r[0]))
                    self.conn.commit()  # 更新该条记录
            else:
                pass
        except Exception as error:
            print error
            write_log([error, '\n'])
            return -1

        try:  # 过去曾经出现过的回答，并且今天还没有更新过
            self.cursor.execute("SELECT * FROM library WHERE today=? and record>0 and post=0 ORDER BY agree DESC", (self.today,))
            ret = self.cursor.fetchall()
            old_answer = ''
            old_count = len(ret)
            if ret:
                for r in ret:
                    link = "https://www.zhihu.com/question/{}/answer/{}".format(r[2], r[3])
                    old_answer += '[%s][%s]<a href="%s" target="_blank">%s</a>\n' % (r[6], r[4], link, r[5])
                    self.cursor.execute("UPDATE library SET post=? WHERE id=?", (r[8] + 1, r[0]))
                    self.conn.commit()
            else:
                pass
        except Exception as error:
            print error
            write_log([error, '\n'])
            return -1

        try:  # 今日高赞答案，并且今天还没有更新过
            self.cursor.execute("SELECT * FROM library WHERE today=? and agree>5000 and post=0 ORDER BY agree DESC", (self.today,))
            ret = self.cursor.fetchall()
            high_answer = ''
            high_count = len(ret)
            if ret:
                for r in ret:
                    link = "https://www.zhihu.com/question/{}/answer/{}".format(r[2], r[3])
                    high_answer += '[%s][%s]<a href="%s" target="_blank">%s</a>\n' % (r[6], r[4], link, r[5])
                    self.cursor.execute("UPDATE library SET post=? WHERE id=?", (r[8] + 1, r[0]))
                    self.conn.commit()
        except Exception as error:
            print error
            write_log([error, '\n'])
            return -1

        head_content = u'今日热门回答共{}个，历史热门回答{}个，今日高赞回答{}个'.format(new_count, old_count, high_count)
        more = '\n<!--more-->'
        content = head_content + more + u'<strong>今日热门回答</strong>\n' + new_answer + more + u'<strong>今日高赞回答</strong>\n' + high_answer + more + u'<strong>历史热门回答</strong>\n' + old_answer
        return content

    def __del__(self):
        self.cursor.close()
        self.conn.close()
        content = "[{}] 程序结束运行.".format(timer())
        print content

      
if __name__ == "__main__":
    wp = WordPress()
    text = wp.rules()  # 加载文章正文
    s = wp.submit(text)  # 发布更新
    del wp
    if s:
        content = u"[{}] 文章发布成功.".format(timer())
        write_log([content.encode('utf8'), '\n'])
    else:
        content = u"[{}] 文章发布失败.".format(timer())
        write_log([content.encode('utf8'), '\n'])
