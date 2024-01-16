import scrapy
import pymongo
import re

import unicodedata
from html import unescape


#base spider required to unify process of getting urls need to be scraped by other fulltext spiders
class AfulltextSpider(scrapy.Spider):

    def start_requests(self):
        newstoparse = self.get_urls_from_database()
        for doc in newstoparse:
            meta = {'doc_id': doc["_id"]}
            url = doc["url"]
            yield scrapy.Request(url=url, callback=self.parse, meta=meta)

    def get_urls_from_database(self, regexpatternStr = ""):
        self.client = pymongo.MongoClient(self.settings.get("MONGODB_URI"), self.settings.get("MONGODB_PORT"))
        self.db = self.client[self.settings.get("MONGODB_DATABASE")]
        cursor = self.db[self.settings.get("MONGODB_TABLE")].find({
            "$and": [
                {"url": {"$regex": regexpatternStr}},
                {"descriptionfull": ""}
            ]
        })
        documentsArr = [document for document in cursor]
        return documentsArr

    def update_valuesindatabase(self, doc_id, keyValueToUpdateDc: dict):
        #keyValueDc = {"descriptionfull": descriptionfull, "author": author} and etc...
        self.db[self.settings.get("MONGODB_TABLE")].update_one({"_id": doc_id}, {"$set": keyValueToUpdateDc})
        self.log(f"OK - updated document _id {doc_id}.")

    def update_cleanfromtags(self, descriptionfull):
        #cleaning from tags excluding <a href=>
        descriptionfull = re.sub(r'<(?!(a\s|/a\s).*?href=["\'](http.*?))[^>]*?>', '', descriptionfull)#remove all tags from the text, but save <a> tags with content of that
        #descriptionfull = re.sub(r'<(?!a\s.*?href=["\'](?:http.*?)")[^>]*?>', '', descriptionfull).strip()#remove all <a> tags from text, excluding only <a
        #descriptionfull = re.sub(r'<(?!(?:a\s[^>]*?href=[\'"]).*?[\'"]).*?>', '', descriptionfull).strip()
        descriptionfull = re.sub(r'<(?!(?:a\s[^>]*?href=[\'"]http).*?[\'"]).*?>', '', descriptionfull)#remove all <a> tags from text, that dont start from http (provides outside from the domain)
        descriptionfull = re.sub(r'<a(?:\s+(?!href=)[^>]+)?\s*href=["\'](https?://[^"\']+)["\'][^>]*>', r'<a href="\1">', descriptionfull)#remove all other attributes from <a> elements excluding href= attribute and content of that
        descriptionfull = re.sub(r'\n\n+', '.', descriptionfull)
        if descriptionfull:
            descriptionfull = unicodedata.normalize("NFKD", descriptionfull) # delete unicode symbols like \xa0 and etc
            descriptionfull = unescape(descriptionfull)#unescape html entities like ... .replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return descriptionfull.strip()

    def closed(self, reason):
        if self.client:
            self.client.close()

        self.log(f'Spider closed: {reason}')