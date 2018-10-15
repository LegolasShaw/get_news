# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GetNewFromSinaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #news_url = scrapy.Field()
    news_type = scrapy.Field()
    news_content = scrapy.Field()


    pass
