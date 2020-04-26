# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import quote
import lxml
from jdselenium.items import JdseleniumItem



class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['www.jd.com']
    base_url = 'https://search.jd.com/Search?keyword='

    def start_requests(self):
        for keyword in self.settings.get('KEYWORDS'):
            for page in range(1,self.settings.get('MAX_PAGE') + 1):
                url = self.base_url + quote(keyword)
                yield scrapy.Request(url=url,callback=self.parse,meta={'page':page},dont_filter=True)

    def parse(self, response):
        # 1.解析本页面
        li_blocks = response.xpath('//div[@id="J_goodsList"]/ul[contains(@class,"gl-warp")]/li[@class="gl-item"]')
        print ('========',len(li_blocks),"条数据======")
        for each_li in li_blocks:
            goods_item = JdseleniumItem()
            name_block = each_li.xpath('div[@class="gl-i-wrap"]/div[contains(@class,"p-name")]/a/em')[0]
            goods_item['name'] = name_block.xpath('string(.)').extract_first().strip()
            comments_block = each_li.xpath('div[@class="gl-i-wrap"]/div[@class="p-commit"]/strong')[0]
            goods_item['comments'] = comments_block.xpath('string(.)').extract_first()
            goods_item['price'] = each_li.xpath('div[@class="gl-i-wrap"]/div[@class="p-price"]/strong/i/text()').extract_first()
            goods_item['saleshop'] = each_li.xpath('div[@class="gl-i-wrap"]/div[@class="p-shop"]/span/a/text()').extract_first()
            img_url = each_li.xpath('div[@class="gl-i-wrap"]/div[@class="p-img"]/a/img/@src').extract_first()
            goods_item['imgurl'] = 'https:' + img_url
            # print (dict(goods_item))
            yield goods_item



