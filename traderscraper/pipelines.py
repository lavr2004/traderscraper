# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo

#
class TraderscraperPipeline:

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri=crawler.settings.get('MONGODB_URI'),
            mongodb_port=crawler.settings.get('MONGODB_PORT'),
            mongodb_database=crawler.settings.get('MONGODB_DATABASE'),
            mongodb_table=crawler.settings.get('MONGODB_TABLE')
        )

    def __init__(self, mongodb_uri, mongodb_port, mongodb_database, mongodb_table):
        self.conn = pymongo.MongoClient(mongodb_uri, mongodb_port)
        self.db = self.conn[mongodb_database]
        self.collection = self.db[mongodb_table]

        self.db[mongodb_table].delete_many({})#clear the database table after restart

        #self.collection.create_index([("url", pymongo.TEXT)], name='unique_index', default_language='english')

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.conn.close()
