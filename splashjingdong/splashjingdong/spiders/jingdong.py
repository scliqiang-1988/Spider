# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import quote
from scrapy_splash import SplashRequest
from splashjingdong.items import SplashjingdongItem
import random

script = """
function main(splash, args)
    splash.images_enabled = false
    assert(splash:go(args.url))
    assert(splash:wait(args.wait))
    js = string.format("document.querySelector('div#J_bottomPage>span.p-skip>input.input-txt').value=%d;document.querySelector('div#J_bottomPage>span.p-skip>a.btn.btn-default').click()", args.page)
    splash:evaljs(js)
    assert(splash:wait(args.wait))
    splash:runjs("document.querySelector('div#J_bottomPage>span.p-skip>input.input-txt').scrollIntoView(true)")
    assert(splash:wait(args.wait))
    return splash:html()
end
"""

class JingdongSpider(scrapy.Spider):
    name = 'jingdong'
    allowed_domains = ['www.jd.com']
    base_url = 'https://search.jd.com/Search?keyword='

    def start_requests(self):
        for keyword in self.settings.get('KEYWORDS'):
            for page in range(1,self.settings.get('MAX_PAGE')+1):
                url = self.base_url + quote(keyword)
                yield SplashRequest(url, callback=self.parse, endpoint='execute',args={'lua_source':script,'page':page,'wait':random.randint(4,6)})

    def parse(self, response):
        li_blocks = response.xpath('//div[@id="J_goodsList"]/ul[contains(@class,"gl-warp")]/li[@class="gl-item"]')
        print(response.request.url,'========', len(li_blocks), "条数据======")
        for each_li in li_blocks:
            goods_item = SplashjingdongItem()
            name_block = each_li.xpath('div[@class="gl-i-wrap"]/div[contains(@class,"p-name")]/a/em')[0]
            goods_item['name'] = name_block.xpath('string(.)').extract_first().strip()
            comments_block = each_li.xpath('div[@class="gl-i-wrap"]/div[@class="p-commit"]/strong')[0]
            goods_item['comments'] = comments_block.xpath('string(.)').extract_first()
            goods_item['price'] = each_li.xpath(
                'div[@class="gl-i-wrap"]/div[@class="p-price"]/strong/i/text()').extract_first()
            goods_item['saleshop'] = each_li.xpath(
                'div[@class="gl-i-wrap"]/div[@class="p-shop"]/span/a/text()').extract_first()
            img_url = each_li.xpath('div[@class="gl-i-wrap"]/div[@class="p-img"]/a/img/@src').extract_first()
            goods_item['imgurl'] = 'https:' + img_url
            # print (dict(goods_item))
            yield goods_item
