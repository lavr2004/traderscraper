import scrapy
from scrapy.crawler import CrawlerProcess
import pymongo

import unicodedata
import re


class CointelegraphcomfulltextSpider(scrapy.Spider):
    name = "cointelegraphcomfulltext"

    allowed_domains = ["cointelegraph.com"]
    start_urls = ["https://cointelegraph.com"]

    def start_requests(self):
        # urls = await self.get_urls_from_database()
        documents = self.get_urls_from_database()
        for doc in documents:
            meta = {'doc_id': doc["_id"]}
            url = doc["url"]
            yield scrapy.Request(url=url, callback=self.parse, meta=meta)
        # for url in urls:
        #     yield scrapy.Request(url=url, callback=self.parse)

    def get_urls_from_database(self):
        # Подключаемся к базе данных и получаем ссылки на новости
        # client = AsyncIOMotorClient(self.settings.get("MONGODB_URI"))
        self.client = pymongo.MongoClient(self.settings.get("MONGODB_URI"), self.settings.get("MONGODB_PORT"))
        self.db = self.client[self.settings.get("MONGODB_DATABASE")]
        # cursor = db[self.settings.get("MONGODB_TABLE")].find({}, {'url': 1})
        cursor = self.db[self.settings.get("MONGODB_TABLE")].find({
            "$and": [
                {"url": {"$regex": "coinjournal.net"}},
                {"descriptionfull": ""}
            ]
        })
        # urls = [document['url'] async for document in cursor]
        documentsArr = [document for document in cursor]
        # client.close()
        # return urls
        return documentsArr

    def parse(self, response):
        # parse required content
        content = response.css("div.post-article-content").get()

        clean_text = re.sub(r'<(?!(a\s|/a\s).*?href=["\'](http.*?))[^>]*?>', '', content).strip()
        clean_text = re.sub(r'\n\n+', '.', clean_text)
        if clean_text:
            clean_text = clean_text.split("Share this article")[0].strip()
            clean_text = unicodedata.normalize("NFKD", clean_text)  # delete unicode symbols like \xa0 and etc

        if clean_text:
            # Обновление документа в MongoDB
            doc_id = response.meta['doc_id']

            # client = AsyncIOMotorClient(self.settings.get("MONGODB_URI"))
            # db = client[self.settings.get("MONGODB_DATABASE")]
            # collection = db[self.settings.get("MONGODB_TABLE")]

            self.db[self.settings.get("MONGODB_TABLE")].update_one({"_id": doc_id}, {"$set": {"descriptionfull": clean_text}})
            self.log(f"Документ с _id {doc_id} обновлен.")

            # client.close()

    def closed(self, reason):
        if self.client:
            self.client.close()

        self.log(f'Spider closed: {reason}')


if __name__ == "__main__":
    # client = pymongo.MongoClient("mongodb://localhost:27017/")
    # db = client["tradescraper"]
    # collection = db["news"]
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    process.crawl(CointelegraphcomfulltextSpider)
    process.start()