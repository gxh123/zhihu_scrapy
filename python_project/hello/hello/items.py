# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


# class HelloItem(scrapy.Item):
#     # define the fields for your item here like:
#     name = scrapy.Field()
#     # pass

# class TopicsItem(scrapy.Item):   #话题广场界面，可以获取大话题的名字，id
#     data_type = scrapy.Field()
#     topic_name = scrapy.Field()
#     topic_id = scrapy.Field()
#
# class TopicItem(scrapy.Item):    #大话题界面，可以获取子话题的名字，描述，链接
#     data_type = scrapy.Field()
#     subTopic_name = scrapy.Field()
#     subTopic_summary = scrapy.Field()
#     subTopic_url = scrapy.Field()
#
# class SubTopicItem(scrapy.Item): #子话题界面，可以获取问题与答案
#     data_type = scrapy.Field()
#     topic_url = scrapy.Field()
#     followers_num = scrapy.Field()
#     top_answers = scrapy.Field()
#     next_page_url = scrapy.Field()

class TopicItem(scrapy.Item):
    type = scrapy.Field()
    topic_id = scrapy.Field()               #话题id
    topic_name = scrapy.Field()             #话题名
    topic_description = scrapy.Field()      #话题描述

class QuestionItem(scrapy.Item):
    type = scrapy.Field()
    question_id = scrapy.Field()            #问题id
    topic_id = scrapy.Field()               #话题id
    question_title = scrapy.Field()         #问题标题
    question_content = scrapy.Field()       #问题具体内容

class UserItem(scrapy.Item):
    type = scrapy.Field()
    # user_id = scrapy.Field()              #页面没有用户id
    user_name = scrapy.Field()              #名字
    user_avatar = scrapy.Field()            #头像
    user_gender = scrapy.Field()            #性别
    user_short_description = scrapy.Field() #一句话描述
    user_long_description = scrapy.Field()  #个人简介
    user_location = scrapy.Field()          #居住地
    user_job = scrapy.Field()               #工作
    user_business = scrapy.Field()          #行业
    user_school = scrapy.Field()            #学校

class AnswerItem(scrapy.Item):
    type = scrapy.Field()
    question_id = scrapy.Field()            #所回答的问题的id
    answer_id = scrapy.Field()              #答案id
    answerer_name = scrapy.Field()          #回答者名字
    answer_content = scrapy.Field()         #答案内容
    answer_agreements = scrapy.Field()      #答案赞数
    answer_edit_time = scrapy.Field()       #编辑时间




