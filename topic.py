#coding=utf-8

# Copyright (C) 2016 Tian Gao
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

import MySQLdb
from bs4 import BeautifulSoup
import json
import re
import time
from math import ceil
import logging
import threading
import Queue
import ConfigParser

from util import get_content


class UpdateOneTopic(threading.Thread):
    def __init__(self,queue):
        self.queue = queue
        threading.Thread.__init__(self)

        cf = ConfigParser.ConfigParser()
        cf.read("config.ini")
        
        host = cf.get("db", "host")
        port = int(cf.get("db", "port"))
        user = cf.get("db", "user")
        passwd = cf.get("db", "passwd")
        db_name = cf.get("db", "db")
        charset = cf.get("db", "charset")
        use_unicode = cf.get("db", "use_unicode")

        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
        self.cursor = self.db.cursor()
        
    def run(self):
        while not self.queue.empty():
            t = self.queue.get()
            link_id = t[0]
            count_id = t[1]
            self.find_new_question_by_topic(link_id,count_id)

    def find_question_by_link(self,topic_url,count_id):
        content = get_content(topic_url,count_id)

        if content == "FAIL":
            return 0

        soup = BeautifulSoup(content)

        questions = soup.findAll('div',attrs={'class':'feed-item'})

        i = 0
        p_str = 'INSERT IGNORE INTO QUESTION (NAME, LINK_ID, FOCUS, ANSWER, LAST_VISIT, ADD_TIME, TOP_ANSWER_NUMBER, ACTIVATE, REVIEW, FIRST_COMMENT) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        anser_list = []
        time_now = int(time.time())

        for question in questions:
            # Do not add questions that are more than 5 days old
            quesTag = question.find('span', attrs={'class':'time'})
            if quesTag is not None:
                quesTime = quesTag.get_text()
            else:
                break
            m = re.search(u'周|月|年', quesTime)
            if m is not None:
                break

            quesLink = question.find('a', attrs={'class':'question_link'})
            tem_text = quesLink.get_text()
            tem_id = quesLink.get('href')
            tem_id = tem_id.replace('/question/','')

            anser_list = anser_list + [(tem_text, int(tem_id), 0, 0, 0, time_now, 0, 0, 0, 0)]

        self.cursor.executemany(p_str,anser_list)

        return len(anser_list)

    def find_new_question_by_topic(self,link_id,count_id):
        new_question_amount_total = 0
        for i in range(1,7):
            topic_url = 'http://www.zhihu.com/topic/' + link_id + '/questions?page=' + str(i)
            new_question_amount_one_page = self.find_question_by_link(topic_url,count_id)
            new_question_amount_total = new_question_amount_total + new_question_amount_one_page

            if new_question_amount_one_page <= 2:
                break
        priority = (120 - new_question_amount_total) / 10
   
        if count_id % 2 == 0:
            print str(count_id) + " , " + self.getName() + " Finshed TOPIC " + link_id + ", page " + str(i) + " ; Add " + str(new_question_amount_total) + " questions." + "Set PRIORITY to " + str(priority)

        time_now = int(time.time())
        sql = "UPDATE TOPIC SET LAST_VISIT = %s, PRIORITY = %s WHERE LINK_ID = %s"
        self.cursor.execute(sql,(time_now,priority,link_id))

class UpdateTopics:
    def __init__(self):
        cf = ConfigParser.ConfigParser()
        cf.read("config.ini")
        
        host = cf.get("db", "host")
        port = int(cf.get("db", "port"))
        user = cf.get("db", "user")
        passwd = cf.get("db", "passwd")
        db_name = cf.get("db", "db")
        charset = cf.get("db", "charset")
        use_unicode = cf.get("db", "use_unicode")

        self.topic_thread_amount = int(cf.get("topic_thread_amount","topic_thread_amount"))

        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
        self.cursor = self.db.cursor()

    def run(self):
        time_now = int(time.time())
        before_last_vist_time = time_now

        queue = Queue.Queue()
        threads = []

        i = 0

        sql = "SELECT LINK_ID FROM TOPIC WHERE LAST_VISIT < %s - PRIORITY * 12 * 3600 ORDER BY PRIORITY, LAST_VISIT"
        self.cursor.execute(sql, (before_last_vist_time,))
        results = self.cursor.fetchall()
            
        for row in results:
            link_id = str(row[0])

            queue.put([link_id, i])
            i = i + 1

        for i in range(self.topic_thread_amount):
            threads.append(UpdateOneTopic(queue))

        for i in range(self.topic_thread_amount):
            threads[i].start()

        for i in range(self.topic_thread_amount):
            threads[i].join()

        self.db.close()

        print 'All task done'

if __name__ == '__main__':
    topic_spider = UpdateTopics()
    topic_spider.run()

