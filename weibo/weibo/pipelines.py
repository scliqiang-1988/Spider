# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re, time
import logging
import pymongo
from scrapy.conf import settings

from weibo.items import *

class TimePipeline:
    def process_item(self,item,spider):
        if isinstance(item,UserItem) or isinstance(item,WeiboItem):
            now = time.strftime('%Y-%m-%d %H:%M',time.localtime())
            item['crawled_at'] = now
        return item

class WeiboPipeline:
    def parse_time(self, date):
        if re.match('刚刚',date):
            date = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
        if re.match('\d+分钟前',date):
            minute = re.match('(\d+)',date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time() - float(minute) * 60))
        if re.match('\d+小时前',date):
            hour = re.match('(\d+)',date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time() - float(hour) * 60 * 60))
        if re.match('昨天.*',date):
            date = re.match('昨天(.*)',date).group(1).strip()
            date = time.strftime('%Y-%m-%d',time.localtime(time.time) - 24 * 60 * 60 + ' ' + date)
        if re.match('\d{2}-\d{2}',date):
            date = time.strftime('%Y-',time.localtime()) + date + ' 00:00'
        return date

    def process_item(self,item,spider):
        if isinstance(item, WeiboItem):
            if item.get('created_at'):
                item['created_at'] = item['created_at'].strip()
                item['created_at'] = self.parse_time(item.get('created_at'))
            if item.get('pictures'):
                item['pictures'] = [pic.get('url') for pic in item.get('pictures')]

        return item
'''
class MongoPipeline(object):
    def __init__(self):
        self.host = settings['MONGO_URL']
        self.port = settings['MONGO_PORT']
        db_name = settings['MONGO_DATABASE']
        client = pymongo.MongoClient('mongodb://{}:{}@{}:{}'.format(settings['MONGO_USER'],settings['MONGO_PASSWORD'],settings['MONGO_URL'],settings['MONGO_PORT']))
        self.db = client[db_name]
        # self.doc = db[settings['MONGODB_DOCNAME']]

    def process_item(self, item, spider):
        if isinstance(item, UserItem) or isinstance(item, WeiboItem):
            self.db[item.collection].insert(dict(item))
            # self.db[item.collection].update({'id': item.get('id')}, {'$set': item}, True)
        # blog_item = dict(item)
        # self.doc.insert(blog_item)
        return item
'''
class MongoPipeline:
    def __init__(self,mongo_url,mongo_port,mongo_user,mongo_password,mongo_db):
        self.mongo_url = mongo_url
        self.mongo_port = mongo_port
        self.mongo_user = mongo_user
        self.mongo_password = mongo_password
        self.mongo_db = mongo_db


    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
            mongo_port = crawler.settings.get('MONGO_PORT'),
            mongo_user = crawler.settings.get('MONGO_USER'),
            mongo_password = crawler.settings.get('MONGO_PASSWORD'),
            mongo_db = crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self,spider):
        connectstr = 'mongodb://{}:{}@{}:{}'.format(self.mongo_user, self.mongo_password, self.mongo_url,self.mongo_port)
        self.client = pymongo.MongoClient(connectstr)
        # self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]
        self.db[UserItem.collection].create_index([('id',pymongo.ASCENDING)])
        self.db[WeiboItem.collection].create_index([('id',pymongo.ASCENDING)])

    def close_spider(self,spider):
        self.client.close()

    def process_item(self,item,spider):
        if isinstance(item, UserItem) or isinstance(item,WeiboItem):
            print ('UserItem...process_spider')
            # self.db[item.collection].insert(dict(item))
            item_dict = dict(item)
            self.db[item.collection].update({'id':item.get('id')},{'$set':item}, True)
        if isinstance(item,UserRalationItem):
            self.db[item.collection].update(
                {'id':item.get('id')},
                {'$addToSet':
                     {
                         'follows':{'$each':item['follows']},
                         'fans':{'$each':item['fans']}
                     }
                },True)
        return item






