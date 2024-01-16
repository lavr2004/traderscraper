# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TraderscraperItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    url = scrapy.Field()
    datepost = scrapy.Field()
    category = scrapy.Field()
    viewscount = scrapy.Field()
    descriptionshort = scrapy.Field()
    descriptionfull = scrapy.Field()
    author = scrapy.Field()

    dateparse = scrapy.Field()

    refkey = scrapy.Field()
