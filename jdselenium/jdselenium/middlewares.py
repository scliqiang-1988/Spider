# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from scrapy.http import HtmlResponse
from logging import getLogger
import time


class JdseleniumSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class JdseleniumDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class SeleniumMiddleware(object):
    def __init__(self, timeout=None):
        self.logger = getLogger(__name__)
        self.timeout = timeout
        '''
        options = webdriver.ChromeOptions()
        prefs = {
            'profile.managed_default_content_settings': {'images': 2}
        }

        options.add_experimental_option('prefs', prefs)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome(options=options)
        '''
        # 直接使用PhantomJS
        self.browser = webdriver.PhantomJS()
        # self.browser.maximize_window()
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def __del__(self):
        self.browser.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            timeout = crawler.settings.get('SELENIUM_TIMEOUT')
        )

    def process_request(self,request,spider):
        """
        在下载器中间件中对接selenium，输出页面源代码之后，构造htmlresponse对象，直接返回给spider解析页面，提取数据，不执行下载器下载页面动作
        :param request:
        :param spider:
        :return:
        """
        # print("selenium is starting...")
        page = request.meta.get('page',1)
        try:
            if page < 2:
                self.browser.get(request.url)
            else:
                # 后续的页面均通过下方的跳转到指定页面来请求
                page_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//div[@id="J_bottomPage"]/span[@class="p-skip"]/input')))
                submit_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@id="J_bottomPage"]/span[@class="p-skip"]/a[contains(@class,"btn")]')))
                page_input.clear()
                page_input.send_keys(page)
                # 点击按钮跳转到指定页码页面
                submit_btn.click()

            # 等待本页面加载完毕后获取页面内容返回
            # 滑动到页面最下部，让本页数据加载完
            page_div = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="J_bottomPage"]')))
            self.browser.execute_script("arguments[0].scrollIntoView();", page_div)
            # 这个地方必须暂停会儿，不然只能获取到前30条数据，拿不到后30条数据
            time.sleep(5)
            last_product = WebDriverWait(self.browser, 30).until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@id="J_goodsList"]/ul[contains(@class,"gl-warp")]/li[last()]')))

            return HtmlResponse(url=request.url,body=self.browser.page_source,request=request,encoding='utf8',status=200)
        except TimeoutException:
            return HtmlResponse(url=request.url,status=500,request=request)

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


