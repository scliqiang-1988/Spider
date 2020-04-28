# -*- coding:utf-8 -*-
__author__ = 'LiQiang'
__date__ = '2020/4/23 11:12'

import json
import pymongo
from mitmproxy import ctx

def response(flow):
	client = pymongo.MongoClient('mongodb://root:123456@192.168.0.104:27017/')
	db = client['spider']
	collection = db['liepin']
	# 这里的页面url可以通过charles抓取获得
	url = 'app-tongdao.liepin.cn/a/t/job/recommend-pages.json'
	if url in flow.request.url:
		text = flow.response.text
		data = json.loads(text)
		items = data.get('data').get('datas')
		for item in items:
			result = {
				'job_id':item.get('job_id'),
				'title':item.get('title'),
				'company':item.get('company'),
				'salary':item.get('salary'),
                'publishdate':item.get('date'),
                'address':item.get('dq'),
                'jobcard_tags':item.get('jobCardTags')
			}
			ctx.log.info(str(result))
			collection.insert(result)