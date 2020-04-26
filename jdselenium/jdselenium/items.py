# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdseleniumItem(scrapy.Item):
    """
    名称、价格、评价数、在售商店名、图片url
    """
    name = scrapy.Field()
    comments = scrapy.Field()
    price = scrapy.Field()
    saleshop = scrapy.Field()
    imgurl = scrapy.Field()



