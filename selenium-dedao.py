# -*- coding:utf-8 -*-
__author__ = 'LiQiang'
__date__ = '2020/4/23 17:21'

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import lxml.html
import pymongo
import time


client = pymongo.MongoClient('mongodb://root:123456@192.168.0.104:27017/')
db = client['spider']
collection = db['dedao']


def parse(text):
	global collection
	selector = lxml.html.fromstring(text)

	# next_page = selector.xpath('//svg[contains(@class,"right-rec") and contains(@class,"right-active")]')

	next_page = selector.xpath(
		'//div[@class="page-select"]/div[contains(@class,"page-active")]/following-sibling::div[contains(@class,"page-normal")]')
	print("next_page:", next_page)

	items = selector.xpath('//ul[@class="pro-list"]/li[@class="pro-detail"]')
	print(len(items))
	results = []

	for item in items:
		res_dict = {}
		res_dict['title'] = item.xpath('div[@class="iget-pro-display"]//div[@class="pro-info"]/p[@property="name"]/a/text()')[0].strip()

		if item.xpath('div[@class="iget-pro-display"]//h3[@class="pro-layer"]/span/text()'):
			res_dict['status'] = item.xpath('div[@class="iget-pro-display"]//h3[@class="pro-layer"]/span/text()')[
				0].strip()
		elif item.xpath('div[@class="iget-pro-display"]//p[@class="pro-layer"]/span/text()'):
			res_dict['status'] = item.xpath('div[@class="iget-pro-display"]//p[@class="pro-layer"]/span/text()')[
				0].strip()

		# res_dict['status'] = item.xpath('div[@class="iget-pro-display"]//h3[@class="pro-layer"]/span/text()')[0].strip()

		res_dict['url'] = item.xpath('div[@class="iget-pro-display"]//div[@class="pro-info"]/p[@property="name"]/a/@href')[0].strip()
		res_dict['introduction'] = item.xpath('div[@class="iget-pro-display"]//p[@class="pro-intro"]/text()')[0].strip()
		coin = item.xpath('div[@class="iget-pro-display"]//p[@class="pro-coin"]')[0]
		res_dict['coin'] = coin.xpath('string(.)').strip()
		print(res_dict)
		results.append(res_dict)
	# 插入数据库
	# print (results)
	# collection.insert_many(results)
	print ("页面数据解析完成...")
	if next_page:
		return True
	else:
		return False



# 设置不加载图片
options = webdriver.ChromeOptions()
prefs = {
	'profile.managed_default_content_settings':{'images':2}
}

options.add_experimental_option('prefs',prefs)
options.add_experimental_option('excludeSwitches',['enable-automation'])
# options.addArguments("--disable-extensions")


browser = webdriver.Chrome(options=options)
# selenium 的PhantomJS已经废弃，使用headless模式代替
# browser = webdriver.PhantomJS()

url = 'https://www.igetget.com/'
# url = 'https://www.igetget.com/list/%E5%BF%83%E7%90%86%E5%AD%A6/ERytOSNfNcK4'
# 窗口最大化
browser.maximize_window()
browser.get(url)

# 点击 更多 获取全部的主题
more_li = WebDriverWait(browser,30).until(EC.presence_of_element_located((By.XPATH,'//ul[@class="lesson-category"]/li[last()]')))

other_tag = browser.find_element_by_xpath('//li[@class="cg-name"]/div/h4[contains(@class,"len2") and contains(@class,"cg-ch")]')
browser.execute_script("arguments[0].scrollIntoView();", other_tag)
# test = input("暂停等待...")
more_a = browser.find_element_by_xpath('//li[@class="cg-name"]/div/h4[contains(@class,"more")]/a')
more_a.click()

# i = 1
# next_page = browser.find_element_by_xpath('//svg[contains(@class,"right-rec") and contains(@class,"right-active")]')
while True:
	#等待页数输入框加载完成
	page_input = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, '//input[@type="number"]')))

	text = browser.page_source
	# print (text)
	print("解析页面...")
	next_flag = parse(text)
	if not next_flag:
		print("已经没有下一页,获取下一主题...")
		next_themes = browser.find_elements_by_xpath('//ul[@class="category-list"]/li[contains(@class,"cg-active")]/following-sibling::li[contains(@class,"cg-title")]')
		if not next_themes:
			print ('已经没有下一主题，退出')
			break
		else:
			# 点击下一主题，加载页面后解析页面
			next_theme = browser.find_elements_by_xpath('//ul[@class="category-list"]/li[contains(@class,"cg-active")]/following-sibling::li[contains(@class,"cg-title")][1]')
			print ("点击下一主题")
			next_theme[0].click()

	else:
		# 否则滚动到最下面
		conf_btn = WebDriverWait(browser, 30).until(
			EC.presence_of_element_located((By.XPATH, '//ul[@class="pro-list"]/li[last()]')))
		flag_tag = browser.find_element_by_xpath('//ul[@class="pro-list"]/li[last()]')
		browser.execute_script("arguments[0].scrollIntoView();", flag_tag)
		# next_page = browser.find_element_by_xpath('//svg[contains(@class,"right-active")]')
		time.sleep(1)
		# next_page = browser.find_element_by_css_selector('svg.right-rec.right-active')
		next_page = browser.find_elements_by_xpath(
			'//div[@class="page-select"]/div[contains(@class,"page-active")]/following-sibling::div[contains(@class,"page-normal")][1]')
		# print ("点击下一页")
		next_page[0].click()
	# i = i + 1
	time.sleep(3)
	# test = input("请等待")
browser.quit()