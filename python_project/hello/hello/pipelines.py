# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class MySQLStorePipeline(object):

    # pipeline默认调用
    def process_item(self, item, spider):
        connection = pymysql.connect(host=spider.settings['MYSQL_HOST'],
                                     user=spider.settings['MYSQL_USER'],
                                     password=spider.settings['MYSQL_PASSWD'],
                                     db=spider.settings['MYSQL_DBNAME'],
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                # 插入topic
                if item['type'] == 'topic':
                    print ("执行insert topic")
                    sql = "insert into topic(topic_id, topic_name, topic_description) values(%s, %s, %s)"
                    cursor.execute(sql, (item['topic_id'], item['topic_name'], item['topic_description']))

                # 插入user
                elif item['type'] == 'user':
                    print ("执行insert user")
                    print (item['user_name'])
                    sql = "insert into user(user_name, user_avatar, user_gender, user_short_description, user_description, user_location, user_job, user_business, user_school) " \
                          "values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (item['user_name'], item['user_avatar'], item['user_gender'], item['user_short_description'], item['user_long_description'],
                    item['user_location'], item['user_job'], item['user_business'], item['user_school']))

                # 插入question
                elif item['type'] == 'question':
                    print ("执行insert question")
                    sql = "insert into question(question_id, topic_id, title, content) values(%s, %s, %s, %s)"
                    cursor.execute(sql, (item['question_id'], item['topic_id'], item['question_title'], item['question_content']))

                # 插入answer
                elif item['type'] == 'answer':
                        # Read a single record
                    print ("执行insert answer")
                    print(item['answerer_name'])
                    sql = "SELECT `user_id` FROM `user` WHERE `user_name` = %s"
                    cursor.execute(sql, item['answerer_name'])
                    answerer_id_dict = cursor.fetchone()
                    sql = "insert into answer(answer_id, question_id, answerer_id, content, agreements, time) values(%s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (item['answer_id'], item['question_id'], answerer_id_dict['user_id'] ,item['answer_content'] , item['answer_agreements'], item['answer_edit_time']))

            connection.commit() #connection is not autocommit by default. So you must commit

            # with connection.cursor() as cursor:
            #     # Read a single record
            #     sql = "SELECT `topic_id`, `topic_name` FROM `topic`"
            #     cursor.execute(sql)
            #     result = cursor.fetchone()
            #     print(result)
        except Exception, e:
            print Exception, ":", e
        finally:
            connection.close()