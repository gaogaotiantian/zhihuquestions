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

from util import get_content, get_time

class UpdateOneQuestion(threading.Thread):
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
            parameters = self.queue.get()
            link_id = parameters[0]
            count_id = parameters[1]
            self.update(link_id,count_id)

    def update(self,link_id,count_id):
        time_now = int(time.time())
        questionUrl = 'http://www.zhihu.com/question/' + link_id

        content = get_content(questionUrl,count_id)
        if content == "FAIL":
            sql = "UPDATE QUESTION SET LAST_VISIT = %s WHERE LINK_ID = %s"
            self.cursor.execute(sql,(time_now,link_id))
            return

        soup = BeautifulSoup(content)

        # There are 3 numbers in this format
        # Focus, Last Activated and Review
        numbers = soup.findAll('div',attrs={'class':'zg-gray-normal'})

        if len(numbers) != 3:
            print "LINK_ID:" + link_id + "Does not have 3 numbers"
            return
        focus    = numbers[0]
        activate = numbers[1]
        review   = numbers[2]
        # Find out how many people focus this question.
        m = re.search(r'<strong>(.*?)</strong>', str(focus))
        if m == None:
            focus_amount = '0'
        else:
            focus_amount = m.group(1)
        # Find out when is this question last activated
        m = re.search(r'>(.*?)<', str(activate))
        if m == None:
            activate_time = u'Unknown'
        else:
            activate_time = get_time(m.group(1))
        # Find out how many people reviewed this question
        m = re.search(r'<strong>(.*?)</strong>', str(review))
        if m == None:
            review_amount = '0'
        else:
            review_amount = m.group(1)

        # Find out how many people answered this question.
        answer_amount = soup.find('h3',attrs={'id':'zh-question-answer-num'})
        if answer_amount != None:
            answer_amount = answer_amount.get_text().replace(u' 个回答','')
        else:
            answer_amount = soup.find('div',attrs={'class':'zm-item-answer'})
            if answer_amount != None:
                answer_amount = u'1'
            else:
                answer_amount = u'0'

        # Find out the top answer's vote amount.
        top_answer = soup.findAll('span',attrs={'class':'count'})
        if top_answer == []:
            top_answer_votes = 0
        else:
            top_answer_votes = 0
            for t in top_answer:
                t = t.get_text()
                t = t.replace('K','000')
                t = int(t)
                if t > top_answer_votes:
                    top_answer_votes = t

        # Find out the first commend date.
        comment_dates = soup.findAll('a',class_="answer-date-link")
        if comment_dates == []:
            first_comment_time = 0
        else:
            times = map(get_time, comment_dates)
            first_comment_time = min(times)

        # print it to check if everything is good.
        if count_id % 1 == 0:
            print str(count_id) + " , " + self.getName() + " Update QUESTION set FOCUS = " + focus_amount + " , ANSWER = " + answer_amount + ", LAST_VISIT = " + str(time_now) + ", TOP_ANSWER_NUMBER = " + str(top_answer_votes) + " where LINK_ID = " + link_id
        #print str(count_id) + " , " + self.getName() + " Update QUESTION set FOCUS = " + focus_amount + " , ANSWER = " + answer_amount + ", LAST_VISIT = " + str(time_now) + ", TOP_ANSWER_NUMBER = " + str(top_answer_votes) + " where LINK_ID = " + link_id
        
        # Update this question
        sql = "UPDATE QUESTION SET FOCUS = %s , ANSWER = %s, LAST_VISIT = %s, TOP_ANSWER_NUMBER = %s , ACTIVATE = %s, REVIEW = %s , FIRST_COMMENT = %s WHERE LINK_ID = %s"
        self.cursor.execute(sql,(focus_amount,answer_amount,time_now,top_answer_votes,activate_time, review_amount, first_comment_time, link_id))

        # Find out the topics related to this question
        topics = soup.findAll('a',attrs={'class':'zm-item-tag'})
        sql_str = "INSERT IGNORE INTO TOPIC (NAME, LAST_VISIT, LINK_ID, ADD_TIME, PRIORITY) VALUES (%s, %s, %s, %s, %s)"
        topicList = []
        for topic in topics:
            topicName = topic.get_text().replace('\n','')
            topicUrl = topic.get('href').replace('/topic/','')
            #sql_str = sql_str + "('" + topicName + "',0," + topicUrl + "," + str(time_now) + "),"
            topicList = topicList + [(topicName, 0, topicUrl, time_now, 0)]
        
        self.cursor.executemany(sql_str,topicList)


class UpdateQuestions:
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

        self.question_thread_amount = int(cf.get("question_thread_amount","question_thread_amount"))

        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
        self.cursor = self.db.cursor()

    def run(self):
        queue = Queue.Queue()
        threads = []

        time_now = int(time.time())
        before_last_visit_time = time_now - 12*3600
        after_add_time = time_now - 24*3600*14
        after_first_comment = time_now - 24*3600*60

        first_period  = time_now - 6*3600 
        first_date    = time_now - 2*24*3600
        second_period = time_now - 12*3600
        second_date   = time_now - 7*24*3600
        second_focus  = 20
        third_period  = time_now - 24*3600
        third_date    = time_now - 30*24*3600 
        third_focus   = 200
        clean_date    = time_now - 60*24*3600
        # Clean the database before update
        sql = "DELETE from QUESTION WHERE (LAST_VISIT > 0) AND ((FIRST_COMMENT < %s AND FOCUS < %s) OR (FIRST_COMMENT < %s) OR (FIRST_COMMENT = 0 AND ADD_TIME < %s))"
        self.cursor.execute(sql, (third_date, third_focus, clean_date, clean_date))

        sql = "SELECT LINK_ID from QUESTION WHERE (LAST_VISIT = '0') OR (LAST_VISIT < %s AND (FIRST_COMMENT > %s OR (FIRST_COMMENT = 0 AND ACTIVATE > %s))) OR (LAST_VISIT < %s AND FIRST_COMMENT > %s AND FOCUS > %s) OR (LAST_VISIT < %s AND FIRST_COMMENT > %s AND FOCUS > %s) ORDER BY LAST_VISIT"
        self.cursor.execute(sql,(first_period, first_date, first_date, second_period, second_date, second_focus, third_period, third_date, third_focus))
        results = self.cursor.fetchall()
        
        i = 0
        
        for row in results:
            link_id = str(row[0])

            queue.put([link_id, i])
            i = i + 1

        thread_amount = self.question_thread_amount

        for i in range(thread_amount):
            threads.append(UpdateOneQuestion(queue))

        for i in range(thread_amount):
            threads[i].start()

        for i in range(thread_amount):
            threads[i].join()

        self.db.close()

        print 'All task done'


if __name__ == '__main__':
    question_spider = UpdateQuestions()
    question_spider.run()
