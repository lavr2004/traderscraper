import pymongo
from scrapy.exceptions import DropItem

class YourScrapyPipeline:
    def __init__(self, mongo_uri, mongo_db, collection_name):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = collection_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE'),
            collection_name=crawler.settings.get('MONGO_COLLECTION')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.collection_name]

        # Проверка существования индекса перед его созданием
        index_field = "ваше_поле"
        existing_indexes = self.collection.index_information()
        if f"{index_field}_1" not in existing_indexes:
            self.collection.create_index([(index_field, pymongo.ASCENDING)], unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # Обработка данных и вставка в MongoDB
        try:
            self.collection.insert_one(dict(item))
        except pymongo.errors.DuplicateKeyError:
            # Если дубликат, игнорируем и продолжаем
            raise DropItem(f"Duplicate item found: {item}")
        return item
