# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from scrapy.exceptions import DropItem
#
class TraderscraperPipeline:
    #indexfield = "url"
    indexfield = "refkey"

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

        #self.db[mongodb_table].delete_many({})#clear the database table after restart

        #self.collection.create_index([("url", pymongo.TEXT)], name='unique_index', default_language='english')

        #CREATE INDEX IF NOT - get validate if unique index on collection already exists and create this index if not
        existing_indexes = self.collection.index_information()
        if f"{self.indexfield}_1" not in existing_indexes:
            #sparse=True - ignore and drop documents with empty field - indexfield
            #unique=True - every field must be unique
            #pymongo.ASCENDING - data values in index must being sorted - it helps in search
            self.collection.create_index([(self.indexfield, pymongo.ASCENDING)], unique=True, sparse=True)

    def process_item(self, item, spider):
        try:
            self.collection.insert_one(dict(item))
        except pymongo.errors.DuplicateKeyError:
            #version1 - with problem - close current spider if refkey doublicate found - https://stackoverflow.com/questions/46749659/force-spider-to-stop-in-scrapy#:~:text=If%20you%20want%20to%20stop,()%20function%20of%20the%20engine.
            #spider.crawler.engine.close_spider(self, reason='doublicate found')

            #ClosingSpiderOnEvent - version2 - ok - close spider if first refkey doublicate found - https://stackoverflow.com/questions/9699049/how-do-i-stop-all-spiders-and-the-engine-immediately-after-a-condition-in-a-pipe
            spider.close_down = True
            raise DropItem(f"ER - doublicate: {item[self.indexfield]}")
        return item

    def close_spider(self, spider):
        self.conn.close()
