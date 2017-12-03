# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_time = scrapy.Field()
    article_url = scrapy.Field()
    article_url_obj = scrapy.Field()
    front_img_url = scrapy.Field()
    front_img_path = scrapy.Field()
    zan = scrapy.Field();
    comment = scrapy.Field()
    collect = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
