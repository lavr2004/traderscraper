import scrapy

import pymongo
import re
import unicodedata


class CoinjournalfulltextSpider(scrapy.Spider):
    name = "coinjournalfulltext"
    allowed_domains = ["coinjournal.net"]
    start_urls = ["https://coinjournal.net"]

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
        self.client = pymongo.MongoClient(self.settings.get("MONGODB_URI"), self.settings.get("MONGODB_PORT"))
        self.db = self.client[self.settings.get("MONGODB_DATABASE")]
        cursor = self.db[self.settings.get("MONGODB_TABLE")].find({
            "$and": [
                {"url": {"$regex": "coinjournal.net"}},
                {"descriptionfull": ""}
            ]
        })
        documentsArr = [document for document in cursor]
        return documentsArr

    def parse(self, response):
        # parse required content
        # parse fulltext news
        descriptionfull = response.css("div.post-article-content").get()

        descriptionfull = re.sub(r'<(?!(a\s|/a\s).*?href=["\'](http.*?))[^>]*?>', '', descriptionfull).strip()
        descriptionfull = re.sub(r'\n\n+', '.', descriptionfull)
        if descriptionfull:
            descriptionfull = descriptionfull.split("Share this article")[0].strip()
            descriptionfull = unicodedata.normalize("NFKD", descriptionfull)  # delete unicode symbols like \xa0 and etc

        # parse author name
        author = response.text.split('<meta name="author" content="')[1].split('"')[0]

        if descriptionfull:
            # Обновление документа в MongoDB
            doc_id = response.meta['doc_id']

            # client = AsyncIOMotorClient(self.settings.get("MONGODB_URI"))
            # db = client[self.settings.get("MONGODB_DATABASE")]
            # collection = db[self.settings.get("MONGODB_TABLE")]

            self.db[self.settings.get("MONGODB_TABLE")].update_one({"_id": doc_id}, {"$set": {"descriptionfull": descriptionfull, "author": author}, })
            self.log(f"OK - updated document _id {doc_id}.")

            # client.close()

    def closed(self, reason):
        if self.client:
            self.client.close()

        self.log(f'Spider closed: {reason}')