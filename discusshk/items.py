# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Identity, TakeFirst, Join
from dateutil.parser import parse


def remove_double_whitespaces(string):
    return re.sub(r'\s+', ' ', string)


to_int = MapCompose(str, lambda x: x.replace(',', ''), str.strip, int)
clean_str = MapCompose(str, str.strip, remove_double_whitespaces)
clean_id = MapCompose(str, lambda x: x.replace('pid', ''), int)


class CategoryItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()


class TopicItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    category = scrapy.Field()


class ThreadItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    topic = scrapy.Field()


class PostItem(scrapy.Item):
    id = scrapy.Field()
    page = scrapy.Field()
    timestamp = scrapy.Field()
    quotes = scrapy.Field()
    body = scrapy.Field()
    user = scrapy.Field()
    thread = scrapy.Field()


class UserItem(scrapy.Item):
    id = scrapy.Field()
    n_posts = scrapy.Field()
    integrity = scrapy.Field()
    username = scrapy.Field()


class CategoryItemLoader(ItemLoader):
    default_item_class = CategoryItem
    default_output_processor = TakeFirst()

    id_in = to_int
    name_in = clean_str


class TopicItemLoader(ItemLoader):
    default_item_class = TopicItem
    default_output_processor = TakeFirst()

    id_in = to_int
    name_in = clean_str


class ThreadItemLoader(ItemLoader):
    default_item_class = ThreadItem
    default_output_processor = TakeFirst()

    id_in = to_int
    name_in = clean_str


class PostItemLoader(ItemLoader):
    default_item_class = PostItem
    default_output_processor = TakeFirst()

    id_in = clean_id
    timestamp_in = MapCompose(parse)
    quotes_in = clean_id
    body_in = clean_str
    page_in = to_int
    body_out = Join(separator='')
    quotes_out = Identity()


class UserItemLoader(ItemLoader):
    default_item_class = UserItem
    default_output_processor = TakeFirst()

    id_in = to_int
    n_posts_in = to_int
    integrity_in = to_int
    username = clean_str
