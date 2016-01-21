#coding=utf-8
import urllib2
import gzip
import StringIO
import ConfigParser
import time
import re


def get_content(toUrl,count):
    """ Return the content of given url

        Args:
            toUrl: aim url
            count: index of this connect

        Return:
            content if success
            'Fail' if fail
    """

    cf = ConfigParser.ConfigParser()
    cf.read("config.ini")
    cookie = cf.get("cookie", "cookie")

    headers = {
        'Cookie': cookie,
        'Host':'www.zhihu.com',
        'Referer':'http://www.zhihu.com/',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept-Encoding':'gzip'
    }

    req = urllib2.Request(
        url = toUrl,
        headers = headers
    )

    try:
        opener = urllib2.build_opener(urllib2.ProxyHandler())
        urllib2.install_opener(opener)

        page = urllib2.urlopen(req,timeout = 15)
        headers = page.info()
        content = page.read()
    except Exception,e:
        if count % 1 == 0:
            print str(count) + ", Error: " + str(e) + " URL: " + toUrl
        return "FAIL"

    if page.info().get('Content-Encoding') == 'gzip':
        data = StringIO.StringIO(content)
        gz = gzip.GzipFile(fileobj=data)
        content = gz.read()
        gz.close()

    return content

def get_time(timeStr):
    """ Return a time_t(integer) value representing time
        
        Args:
            A string representing time. Possible form:
                昨天 hh:mm
                hh:mm
                YYYY-MM-DD
        Return:
            A integer time_t value that is accurate to days
            If can't match the form, return 0
    """
    if type(timeStr) is not str:
        timeStr = str(timeStr)
    if "昨天" in timeStr:
        return time.time() - 3600*24
    elif ':' in timeStr:
        return time.time()
    elif '-' in timeStr:
        m = re.search('(\d*)-(\d*)-(\d*)', timeStr)
        if m is not None:
            time_st = (int(m.group(1)), int(m.group(2)), int(m.group(3)), 0, 0, 0, 0, 0, 0)
            return time.mktime(time_st)
        else:
            return 0
    else:
        print "error!" + timeStr
        return 0;
if __name__ == "__main__":
    # testcase
    cases = [u"昨天 12:24",
             u"10:30",
             u"2015-12-03",
             u"fdsafe"]
    for case in cases:
        print get_time(case)
