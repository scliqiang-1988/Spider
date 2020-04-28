# -*- coding:utf-8 -*-
__author__ = 'LiQiang'
__date__ = '2020/4/26 10:34'

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import lxml.html
import pymongo
import time
from urllib.parse import quote


client = pymongo.MongoClient('mongodb://root:123456@192.168.0.104:27017/')
db = client['spider']
collection = db['jingdong']


def parse(text):
	global collection
	selector = lxml.html.fromstring(text)

	# next_page = selector.xpath('//svg[contains(@class,"right-rec") and contains(@class,"right-active")]')

	next_page = selector.xpath(	'//div[@id="J_bottomPage"]/span[@class="p-num"]/a[@class="pn-next"]')
	# print("next_page:", next_page)

	items =  selector.xpath('//div[@id="J_goodsList"]/ul[contains(@class,"gl-warp")]/li[@class="gl-item"]')
	print(len(items))
	results = []

	for item in items:
		res_dict = {}

		name_block = item.xpath('div[@class="gl-i-wrap"]/div[contains(@class,"p-name")]/a/em')[0]
		res_dict['name'] = name_block.xpath('string(.)').strip()
		comments_block = item.xpath('div[@class="gl-i-wrap"]/div[@class="p-commit"]/strong')[0]
		res_dict['comments'] = comments_block.xpath('string(.)')
		res_dict['price'] = item.xpath('div[@class="gl-i-wrap"]/div[@class="p-price"]/strong/i/text()')
		res_dict['saleshop'] = item.xpath('div[@class="gl-i-wrap"]/div[@class="p-shop"]/span/a/text()')

		print(res_dict)
		results.append(res_dict)
	# 插入数据库
	# print (results)
	# collection.insert_many(results)
	print ("页面数据解析完成...")
	# if next_page:
	# 	return True
	# else:
	# 	return False



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

# url = 'https://www.igetget.com/'
# url = 'https://www.igetget.com/list/%E5%BF%83%E7%90%86%E5%AD%A6/ERytOSNfNcK4'
keyword = 'iphone'
url = 'https://search.jd.com/Search?keyword=' + quote(keyword)
# 窗口最大化
browser.maximize_window()
browser.get(url)
for page in range(1,5):
	if page == 1:
		browser.get(url)
	else:
		# time.sleep(3)
		# page_div = WebDriverWait(browser, 30).until(
		# 	EC.presence_of_element_located((By.XPATH, '//div[@id="J_bottomPage"]')))
		# browser.execute_script("arguments[0].scrollIntoView();", page_div)

		# xpath_str = '//div[@id="J_bottomPage"]/span[@class="p-num"]/a[@class="curr"]/following-sibling::a[text()={}]'.format(page)
		# print (xpath_str)
		# page_btn = browser.find_element_by_xpath(xpath_str)
		# page_btn.click()

		page_input = WebDriverWait(browser, 30).until(
			EC.presence_of_element_located((By.XPATH, '//div[@id="J_bottomPage"]/span[@class="p-skip"]/input')))
		submit_btn = WebDriverWait(browser, 30).until(
			EC.element_to_be_clickable((By.XPATH, '//div[@id="J_bottomPage"]/span[@class="p-skip"]/a[contains(@class,"btn")]')))
		page_input.clear()
		page_input.send_keys(page)

		submit_btn.click()  # 点击按钮跳转到指定页码页面

	# 等待页数输入框加载完成
	time.sleep(3)
	# page_input = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, '//input[@type="number"]')))
	page_div = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@id="J_bottomPage"]')))
	browser.execute_script("arguments[0].scrollIntoView();", page_div)
	# 这个地方必须暂停会儿，不然只能获取到前30条数据，拿不到后30条数据
	time.sleep(5)
	print (browser.current_url)
	text = browser.page_source
	# print (text)
	print("解析页面...")
	parse(text)
	'''
	next_flag = parse(text)
	if not next_flag:
		print ('已经没有下一页,退出...')
		break
	else:
		next_page = browser.find_elements_by_xpath('//div[@id="J_bottomPage"]/span[@class="p-num"]/a[@class="pn-next"]')
		print("点击下一页")
		next_page[0].click()
		time.sleep(3)
		'''
browser.quit()