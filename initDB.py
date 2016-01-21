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
import re
import time
from bs4 import BeautifulSoup
from util import get_content
import ConfigParser

class Initializer():
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

        self.zh_username = cf.get("zhihu", "username")

        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
        self.cursor = self.db.cursor()
    def run(self):
        url = "http://www.zhihu.com/people/" + self.zh_username + "/topics"
        content = get_content(url, 1)
        time_now = time.time()
        if content == "FAIL":
            print "Fail to open the url:" + url
            return
        else:
            soup = BeautifulSoup(content)
            results = soup.findAll('div', attrs={'class':'zm-profile-section-main'})
            if results == None or len(results) == 0:
                print "No topic is found!"
                return
            for result in results:
                m = re.search(r'topic/(\d*)', str(result))
                if m == None:
                    print "No matching topic"
                    continue
                else:
                    link_id = m.group(1)

                m = re.search(r'<strong>(.*?)</strong>', str(result))
                if m == None:
                    print "No topic name!"
                    continue
                else:
                    name = m.group(1)
                print link_id, name
                sqlcmd = "INSERT IGNORE INTO TOPIC (NAME, LAST_VISIT, LINK_ID, ADD_TIME) VALUES (%s, %s, %s, %s)" 
                self.cursor.execute(sqlcmd, (name, 0, link_id, time_now))
if __name__ == "__main__":
    i = Initializer()
    i.run()
