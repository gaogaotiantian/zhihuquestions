#coding=utf-8
import MySQLdb
import ConfigParser
import time
import json
class QuestionData():
    def __init__(self, l=[]):
        self.data = {}
        if len(l) == 8:
            # Input is a single row in database
            self.data["NAME"]              = '<a href="http://www.zhihu.com/question/' + str(l[0]) + '">' + l[1].encode('utf8') + '</a>'
            if round(float(l[2])/max(1, l[3]), 2) > 10:
                self.data["NAME"]         += '<span class="hv">Value</span>'
            elif round(float(l[2])/max(1, l[3]), 2) > 5:
                self.data["NAME"]         += '<span class="lv">Value</span>'
            if l[2] > 1000 or l[5] > 10000:
                self.data["NAME"]         += '<span class="hh">Hot</span>'
            elif l[2] > 500 or l[5] > 5000:
                self.data["NAME"]         += '<span class="lh">Hot</span>'

            self.data["FOCUS"]             = l[2]
            self.data["ANSWER"]            = l[3]
            self.data["FARATIO"]           = round(float(l[2])/max(1, l[3]), 2)
            self.data["TOP_ANSWER_NUMBER"] = l[4]
            self.data["REVIEW"]            = l[5]
            self.data["FIRST_COMMENT"]     = time.strftime("%Y-%m-%d", time.gmtime(l[6]))
            self.data["ACTIVATE"]          = time.strftime("%Y-%m-%d", time.gmtime(l[7]))
        elif len(l) != 0:
            print "Wrong data from single row of database!"

class QuestionDataSet():
    def __init__(self, l = []):
        self.dataset = []
        if len(l) > 0:
            # Input is a list of rows from database
            for d in l:
                newData = QuestionData(d);
                self.dataset.append(newData.data);
    def PrintToJson(self, path):
        with open(path, "w") as f:
            f.write(json.dumps(self.dataset, indent=4))
class DataBase():
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

        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
        self.cursor = self.db.cursor()
    def GetAll(self):
        now_time = time.time()

        after_comment_time = now_time - 24*3600*60
        after_activate     = now_time - 24*3600*5
        within_two_days    = now_time - 24*3600*2

        sqlcmd = "SELECT LINK_ID, NAME, FOCUS, ANSWER, TOP_ANSWER_NUMBER, REVIEW, FIRST_COMMENT, ACTIVATE from QUESTION WHERE (REVIEW > 300 AND FOCUS > 20 AND FIRST_COMMENT > %s AND ACTIVATE > %s) OR (FIRST_COMMENT > %s AND FOCUS > 10) OR (ACTIVATE > %s AND ANSWER < 1 AND FOCUS > 5)ORDER BY FIRST_COMMENT DESC"
        self.cursor.execute(sqlcmd, (after_comment_time, after_activate, within_two_days, within_two_days))
        result = self.cursor.fetchall()
        dataset = QuestionDataSet(result)
        dataset.PrintToJson("./db.json")
        return result
if __name__ == "__main__":
    print "Initialize database..."
    curDB = DataBase()
    print "Start getting data from database..."
    result = curDB.GetAll()
    print "Got data from database and start to print..."
    """
    with open("zhihuquestions.html", "w") as f: 
        ct = 0
        content = ""
        content += '<meta charset="UTF-8">\n'
        content += "<table>\n"
        # Table header
        content += '<tr><td>问题</td><td>关注人数</td><td>答案数</td><td>最高答案赞同数</td><td>浏览人数</td><td>首个评论时间</td><td>上次活跃时间</td></tr>'
        for r in result:
            content += "<tr>\n"
            for idx, data in enumerate(r):
                if idx == 0:
                    link_id = data
                elif idx == 1: # Add link to question
                    content += '<td> <a href="http://www.zhihu.com/question/' + str(link_id) + '">' + data.encode('utf8') + '</a></td>\n'
                elif idx == 6 or idx == 7:
                    content += "<td>" + time.strftime("%Y-%m-%d", time.gmtime(data)) + "</td>\n"
                else:
                    if type(data) is unicode:
                        content += "<td>" + data.encode('utf8') + "</td>\n"
                    else:
                        content += "<td>" + str(data) + "</td>\n"
            content += "</tr>\n"
            f.write(content)
            content = ""
        content += "</table>\n"
        f.write(content)
        content = ""
    """
