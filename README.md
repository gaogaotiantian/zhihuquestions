# zhihuquestions
A web spider for zhihu.com, which is used for [zhihuquestions](http://minkoder.com/zhihuquestions.html).  
This spider can scrape question & topic data from zhihu.com.  

This spider is based on [zhihu-spider](https://github.com/MorganZhang100/zhihu-spider).

## Author
[Tian Gao](https://www.zhihu.com/people/gao-tian-50)

## Run it

### What do you need to run it
- Python 2.7.6 (Maybe it work for other versions.) 
- MySQL
- BeautifulSoup

### How to run it
1. Download the code
1. Set up your database using MySQL
1. Initialize your database using init.sql
1. Find out your cookie of zhihu.com throught browser's developer tool.
1. Modify config.ini
1. If you set up zhihu username and cookies correctly, you may run initDB.py to get all your current focused topics into database as seeds, otherwise you can manually insert some topics in TOPIC as scrape seeds.
1. Use ```python topic.py``` to get topics and questions from zhihu.com
1. Use ```python question.py``` to analyze questions from zhihu.com
1. You have to use both topic.py and questions.py in rotation to make the database grow.

## Warning
You can change thread amount in config.ini to make this spider run faster.  
But your IP may be blocked from zhihu.com if you connect to zhihu.com too frequently.  
You'd better use proxy when you use multi thread mode.

## License
The MIT license.
