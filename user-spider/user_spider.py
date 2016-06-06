import MySQLdb
import ConfigParser
import threading
import time
import Queue
from zhihu import User
class UpdateOneUser(threading.Thread):
    def __init__(self, queue):
        self.queue = queue
        threading.Thread.__init__(self)

        cf = ConfigParser.ConfigParser()
        cf.read('db.ini')

        host = cf.get("db", "host")
        port = int(cf.get("db", "port"))
        user = cf.get("db", "user")
        passwd = cf.get("db", "passwd")
        db_name = cf.get("db", "db")
        charset = cf.get("db", "charset")
        use_unicode = cf.get("db", "use_unicode")

        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
        self.cursor = self.db.cursor()
        self.start_time = time.time()
        self.user_num = 0
    def run(self):
        while not self.queue.empty():
            q = self.queue.get()
            link_id = q
            self.UpdateUserDataByLinkId(link_id)

    def UpdateUserDataByLinkId(self, link_id):
        try:
            user = User(link_id)
        except Exception, e:
            print e
            print "Read " + link_id + " failed!"
            return
        # Update the user's info first
        try : 
            name = user.get_user_id()
            followee = user.get_followees_num()
            follower = user.get_followers_num()
            agree = user.get_agree_num()
            answer = user.get_answers_num()
            last_visit = time.time()
        except Exception, e:
            print "Got an excpetion when reading", link_id 
            print e
            return

        sql = 'UPDATE USER SET NAME = %s, FOLLOWER = %s, FOLLOWEE = %s, AGREE_NUM = %s, ANSWER_NUM = %s, LAST_VISIT = %s WHERE LINK_ID = %s'
        self.cursor.execute(sql, (name, follower, followee, agree, answer, last_visit, link_id))

        # Get his followees
        try:
            new_users = user.get_followees()
            sql = 'INSERT IGNORE INTO USER (NAME, LINK_ID, FOLLOWER, FOLLOWEE, ANSWER_NUM, AGREE_NUM, LAST_VISIT) VALUES (%s, %s, %s, %s, %s, %s, %s)'
            check_sql = 'SELECT EXISTS(SELECT 1 from USER where LINK_ID = %s LIMIT 1)'
            num_we_already_have = 0
            for new_user in new_users:
                link_id = new_user.user_url
                if link_id is not None:
                    if 'https://' in link_id:
                        link_id = link_id.replace('https://', 'http://')
                    self.cursor.execute(check_sql, (link_id))
                    results = self.cursor.fetchall()
                    if results[0][0] == 0:
                        num_we_already_have = 0
                        self.cursor.execute(sql, ('', link_id, 0, 0, 0, 0, 0))
                    else:
                        num_we_already_have = num_we_already_have + 1
                        if num_we_already_have >= 10:
                            break

        except IndexError:
            pass
        except Exception, e:
            print "Got an exception when getting", link_id, "followees" 

        self.user_num += 1
        print "Updated", name, "at", time.strftime("%H:%M:%S", time.localtime(time.time())), "Total number: ", self.user_num, "Average time: ", (time.time() - self.start_time) / self.user_num
            


class UpdateUser:
    def __init__(self):
        cf = ConfigParser.ConfigParser()
        cf.read('db.ini')

        host = cf.get("db", "host")
        port = int(cf.get("db", "port"))
        user = cf.get("db", "user")
        passwd = cf.get("db", "passwd")
        db_name = cf.get("db", "db")
        charset = cf.get("db", "charset")
        use_unicode = cf.get("db", "use_unicode")

        self.thread_amount = 4

        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
        self.cursor = self.db.cursor()
    def run(self):
        queue = Queue.Queue()
        threads = []
        time_now = time.time()
        time_max = time_now - 3600*24
        sql = 'SELECT LINK_ID from USER where LAST_VISIT < %s ORDER BY LAST_VISIT'
        self.cursor.execute(sql, (time_max))
        results = self.cursor.fetchall()

        for row in results:
            link_id = str(row[0])
            if 'https://' in link_id:
                sql = 'DELETE FROM USER where LINK_ID = %s'
                print 'Deleted', link_id
                self.cursor.execute(sql, (link_id))
            else:
                queue.put(link_id)

        for i in range(self.thread_amount):
            threads.append(UpdateOneUser(queue))

        for i in range(self.thread_amount):
            threads[i].start()

        for i in range(self.thread_amount):
            threads[i].join()

        self.db.close()

        print "Finish! Time used: ", time.time() - time_now

if __name__ == "__main__":
    update = UpdateUser()
    update.run()
