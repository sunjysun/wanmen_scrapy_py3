# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WanmenTeacherItem(scrapy.Item):
    ID = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()

class WanmenCourseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ID = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    teacher = scrapy.Field()
    doc = scrapy.Field()

class WanmenLectureChildItem(scrapy.Item):
    ID = scrapy.Field()
    course_id = scrapy.Field()
    name = scrapy.Field()
    order = scrapy.Field()
    video = scrapy.Field()

class WanmenCategoryItem(scrapy.Item):
    ID = scrapy.Field()
    name = scrapy.Field()

class WanmenMajorItem(scrapy.Item):
    ID = scrapy.Field()
    name = scrapy.Field()

class WanmenDocItem(scrapy.Item):
    doc = scrapy.Field()