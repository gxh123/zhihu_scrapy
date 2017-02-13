# -*- coding: utf-8 -*-
import datetime
import random

import scrapy
import time
from scrapy import FormRequest
from scrapy import Request

from hello.items import TopicItem, QuestionItem, UserItem, AnswerItem
# from topic import Topic
# from topics import *
from login import isLogin
from login import login
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import json
import re

class MySpider(scrapy.Spider):
    name = "myspider"

    # start_urls = [
    #     'http://ip.filefab.com/'
    # ]
    #
    # def start_requests(self):
    #     yield Request(
    #         url='http://ip.filefab.com/index.php',
    #         headers=self.set_headers(None),
    #         # cookies=cookielib.LWPCookieJar(filename='cookies')
    #     )
    #
    # def parse(self, response):
    #     print response.body


    start_urls = [
        'https://www.zhihu.com/topics'
    ]

    user_agent_list = [
        'User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko',
        'User-Agent:Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
        'User-Agent:Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
        'User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
        'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
    ]
    #
    def set_headers(self, url):
        # agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
        agent = self.user_agent_list[random.randint(0,7)]
        # print (agent)
        headers = {
            "Host": "www.zhihu.com",
            'User-Agent': agent
        }
        headers['Referer'] = url
        return headers

    def start_requests(self):
        if isLogin():
            print('您已经登录')
        else:
            # account = input('请输入你的用户名\n>  ')
            # secret = input("请输入你的密码\n>  ")
            account = '15728689495'
            secret = 'q12345'
            login(secret, account)
        for url in self.start_urls:
            yield Request(
                url=url,
                headers=self.set_headers('https://www.zhihu.com'),
                cookies=cookielib.LWPCookieJar(filename='cookies')
            )


    def parse(self, response):
        topic_xpath_rule = '//li[@class="zm-topic-cat-item"]/a/text()'
        topic_names = response.selector.xpath(topic_xpath_rule).extract()

        topic_xpath_rule = '//li[@class="zm-topic-cat-item"]/@data-id'
        topic_ids = response.selector.xpath(topic_xpath_rule).extract()

        # for i in range(len(topic_ids)):
        print("取30个话题")
        # for i in range(10):
        for i in range(len(topic_ids)):
            params = {"topic_id": int(topic_ids[i]), "offset": 0, "hash_id": "d17ff3d503b2ebce086d2f3e98944d54"}
            yield FormRequest(
                url='https://www.zhihu.com/node/TopicsPlazzaListV2',
                method='POST',
                # headers=self.set_headers2('https://www.zhihu.com/topics'),
                headers=self.set_headers('https://www.zhihu.com/topics'),
                cookies=cookielib.LWPCookieJar(filename='cookies'),
                # formdata={'method': 'next', 'params': '{"topic_id":988,"offset":0,"hash_id":"d17ff3d503b2ebce086d2f3e98944d54"}'},
                formdata={'method': 'next', 'params': str(params).replace("\'", "\"").replace(" ", "")},
                callback=self.topic_parse,
                meta={'topic_name': topic_names[i]}
            )

    def topic_parse(self, response):
        if response.status in [400, 403, 302]:
            response.request.meta["change_proxy"] = True
            print ("答案抓取出现问题：{url}".format(url=response.request.headers["Referer"]))
            pass
        else:
            # 名字，描述，链接，图片
            json_object = json.loads(response.body_as_unicode())
            json_content = ''.join(json_object['msg'])
            pattern = re.compile('<strong>(.*?)</strong>')
            subtopic_names = re.findall(pattern,json_content)

            pattern = re.compile('<p>(.*?)</p>')
            subtopic_descriptions = re.findall(pattern,json_content)

            pattern = re.compile('<a target="_blank" href="([^"]*)".*?>')
            subtopic_urls = re.findall(pattern,json_content)

            pattern = re.compile('<img src="(.*?)" alt=')
            subtopic_pics = re.findall(pattern,json_content)

            print("subtopic: %s"%len(subtopic_names))
            # for i in range(2):
            for i in range(len(subtopic_names)):
                base_url = "https://www.zhihu.com" + subtopic_urls[i]
                yield Request(
                    # url = base_url + "/top-answers",
                    url=base_url + "/top-answers?page=3",
                    # headers = self.set_headers3(base_url + "/hot"),
                    headers=self.set_headers(base_url + "/hot"),
                    cookies = cookielib.LWPCookieJar(filename='cookies'),
                    callback = self.top_answers_parse,
                )

    # 爬取精华答案页面（获取答案链接）
    def top_answers_parse(self, response):
        if response.body in ["banned", b"{'reason': b'Bad Request', 'status': 400}",
                             "{'reason': b'Bad Request', 'status': 400}",
                             ]:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        else:
            # 获取topic和描述
            # https://www.zhihu.com/topic/19551137/top-answers?page=2
            # print response.url
            end = response.url.rfind("/")
            topic_id = int(response.url[28:end])
            # print topic_id
            # topic_id = int(response.url[28:-12])
            topic_name_xpath_rule = '//h1[@class="zm-editable-content"]/text()'
            topic_name = response.selector.xpath(topic_name_xpath_rule).extract_first()

            topic_description_xpath_rule = '//div[@id="zh-topic-desc"]/div[@class="zm-editable-content"]/text()'
            topic_description = response.selector.xpath(topic_description_xpath_rule).extract_first()
            # print ("topic description")
            # print (topic_description)
            #存入数据库
            topicItem = TopicItem()
            topicItem['type'] = 'topic'
            topicItem['topic_id'] = topic_id
            topicItem['topic_name'] = topic_name
            topicItem['topic_description'] = topic_description
            yield topicItem

            answer_url_xpath_rule = '//div[@class="feed-item feed-item-hook folding"]/link/@href'
            answer_urls_temp = response.selector.xpath(answer_url_xpath_rule).extract()
            answer_urls = ["https://www.zhihu.com" + temp for temp in answer_urls_temp]   #获取答案链接

            for answer_url in answer_urls:
                # print answer_url
                yield Request(
                    url = answer_url,
                    # headers = self.set_headers3(None),
                    headers=self.set_headers(None),
                    cookies = cookielib.LWPCookieJar(filename='cookies'),
                    callback = self.answer_parse,
                    meta={'topic_id': topic_id}
                )
            # print ("取精华答案的第一个")
            # answer_url = answer_urls[0]
            # yield Request(
            #     url = answer_url,
            #     headers = self.set_headers(None),
            #     cookies = cookielib.LWPCookieJar(filename='cookies'),
            #     callback = self.answer_parse,
            # )

    def answer_parse(self, response):
        if response.body in ["banned", b"{'reason': b'Bad Request', 'status': 400}",
                             "{'reason': b'Bad Request', 'status': 400}",
                             ]:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        else:
            # 问题id
            question_id = int(response.url[31:response.url.find('/answer/')])
            # print question_id

            # 问题标题
            question_title_xpath_rule = '//h2[@class="zm-item-title"]/a/text()'
            question_title_temp = response.selector.xpath(question_title_xpath_rule).extract_first()
            question_title = question_title_temp.replace("\n", "")
            # print question_title

            # 问题内容
            question_content_xpath_rule = '//div[@class="zm-editable-content"]/text()'
            question_content_temp = response.selector.xpath(question_content_xpath_rule).extract_first()
            if question_content_temp is not None:
                question_content = question_content_temp.replace("\n", "")
                # print question_content
            else:
                question_content = None
            # 将问题存入数据库
            questionItem = QuestionItem()
            questionItem['type'] = 'question'
            questionItem['question_id'] = question_id
            questionItem['topic_id'] = response.meta['topic_id']
            questionItem['question_title'] = question_title
            questionItem['question_content'] = question_content
            yield questionItem


            # 爬回答者链接
            answerer_url_xpath_rule = '//a[@class="author-link"]/@href'
            answerer_url_temp = response.selector.xpath(answerer_url_xpath_rule).extract_first()
            answerer_url = "https://www.zhihu.com" +  answerer_url_temp  + "/answers"  #获取回答者链接
            # print answerer_url

            # 答案id
            start = response.url.rfind("/") + 1
            answer_id = int(response.url[start:])

            # 答案赞数
            answer_agreements_xpath_rule = '//span[@class="count"]/text()'
            answer_agreements_temp = response.selector.xpath(answer_agreements_xpath_rule).extract_first()
            index = answer_agreements_temp.find('K')
            if  index != -1:
                answer_agreements = int(answer_agreements_temp[:index])*1000
            else:
                answer_agreements = int(answer_agreements_temp)
            # print answer_agreements

            # 答案编辑时间
            answer_date_xpath_rule = '//a[@class="answer-date-link meta-item"]/text()'
            answer_date_temp = response.selector.xpath(answer_date_xpath_rule).extract_first()
            answer_date_str = answer_date_temp[4:]         #注：由于爬的是高赞答案，时间都比较长，所以一般都满足"编辑于 2017-01-11"这个格式，正常答案不一定
            answer_date = datetime.datetime.strptime(answer_date_str, '%Y-%m-%d')


            # 爬答案，(不能用xpath,获取不到内容里的标签，)作为参数传给user_parse函数
            str = response.body_as_unicode()
            pattern = re.compile('<div class="zm-editable-content clearfix">\\n(.+?)\\n</div>')   #注意回车！
            result = pattern.findall(str)
            if len(result) > 0:
                answer_content = result[0]
            else :
                # 少部分时候答案中会有'\n'(不知道为什么)，替换掉再找
                str2 = str.replace("\n","")
                pattern = re.compile('<div class="zm-editable-content clearfix">(.+?)</div>')   #去掉了回车！
                result = pattern.findall(str2)
                answer_content = result[0]

            # 将答案存入数据库
            answerItem = AnswerItem()
            answerItem['type'] = 'answer'
            answerItem['question_id'] = question_id             # 所回答的问题的id
            answerItem['answer_id'] = answer_id                 # 答案id
            answerItem['answer_content'] = answer_content       # 答案内容
            answerItem['answer_agreements'] = answer_agreements # 答案赞数
            answerItem['answer_edit_time'] = answer_date        # 编辑时间
            # yield answerItem

            yield Request(
                url = answerer_url,
                # headers = self.set_headers3(response.url),
                headers=self.set_headers(response.url),
                cookies = cookielib.LWPCookieJar(filename='cookies'),
                callback = self.user_parse,
                meta={'answer_item': answerItem}
            )

            # 爬评论者（前30） 先不爬了，略麻烦
            # 爬评论（前30条）

    def user_parse(self, response):
        if response.body in ["banned", b"{'reason': b'Bad Request', 'status': 400}",
                             "{'reason': b'Bad Request', 'status': 400}",
                             ]:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        else:
            # print response.url
            #获取user数据
            user_name_xpath_rule = '//span[@class="ProfileHeader-name"]/text()'
            user_name = response.selector.xpath(user_name_xpath_rule).extract_first()
            # print (user_name)

            short_description_xpath_rule = '//span[@class="RichText ProfileHeader-headline"]/text()'
            short_description = response.selector.xpath(short_description_xpath_rule).extract_first()

            user_avatar_xpath_rule = '//img[@class="Avatar Avatar--large UserAvatar-inner"]/@src'
            user_avatar = response.selector.xpath(user_avatar_xpath_rule).extract_first()

            user_gender_xpath_rule = '//svg[@class="Icon Icon--male"]'
            if response.selector.xpath(user_gender_xpath_rule).extract_first() is None:
                user_gender = 0
            else:
                user_gender = 1

            data_xpath_rule = '//div[@id="data"]/@data-state'
            data = response.selector.xpath(data_xpath_rule).extract_first()

            pattern = re.compile(r'description":"(.+?)"')
            result = pattern.findall(data)
            user_description = result[0] if len(result) > 0 else None   # 简介，有链接的会取不全，还没解决

            pattern = re.compile(r'job":{"name":"(.+?)"')
            result = pattern.findall(data)
            user_job = result[0] if len(result) > 0 else None           # 工作

            pattern = re.compile(r'business":{"name":"(.+?)"')
            result = pattern.findall(data)
            user_business = result[0] if len(result) > 0 else None      # 行业

            pattern = re.compile(r'locations":\[{"name":"(.+?)"')
            result = pattern.findall(data)
            user_location = result[0] if len(result) > 0 else None      # 所在地

            pattern = re.compile(r'major":{"name":"(.+?)"')
            result = pattern.findall(data)
            user_major = result[0] if len(result) > 0 else None         # 专业

            pattern = re.compile(r'school":{"name":"(.+?)"')
            result = pattern.findall(data)
            user_school = result[0] if len(result) > 0 else None        # 学校

            #将用户存入数据库
            userItem = UserItem()
            userItem['type'] = 'user'
            userItem['user_name'] = user_name           # 名字
            userItem['user_avatar'] = user_avatar       # 头像
            userItem['user_gender'] = user_gender       # 性别
            userItem['user_short_description'] = short_description  # 一句话描述
            userItem['user_long_description'] = user_description    # 个人简介
            userItem['user_location'] = user_location   # 居住地
            userItem['user_job'] = user_job             # 工作
            userItem['user_business'] = user_business   # 行业
            userItem['user_school'] = user_school       # 学校
            yield userItem

            time.sleep(3)  #等user存入数据库

            #将答案存入数据库
            answerItem = response.meta["answer_item"]
            answerItem['answerer_name'] = user_name
            yield answerItem



































