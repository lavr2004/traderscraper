import time

import scrapy
from traderscraper.spiders.afulltextSpider import AfulltextSpider

#TODO: need to find the way for parsing descriptionfull by passing cloudflare and js
class BitcoinmagazinecomfulltextSpider(AfulltextSpider):
    name = "bitcoinmagazinecomfulltext"
    allowed_domains = ["bitcoinmagazine.com"]
    #start_urls = ["https://bitcoinmagazine.com/articles"]

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'traderscraper.selenium_middleware.CustomSeleniumMiddleware': 800,
        },
    }

    def start_requests(self):
        newstoparse = self.get_urls_from_database(self.allowed_domains[0])

        scrapy.Request(url="https://bitcoinmagazine.com/")
        self.log("OK - requested initial page")

        time.sleep(10)
        for doc in newstoparse:
            meta = {'doc_id': doc["_id"]}
            url = doc["url"]
            yield scrapy.Request(url=url, callback=self.parse, meta=meta)

    def parse(self, response):
        time.sleep(10)

        article = response.css("div.l-grid--content-body").get()
        article = self.update_cleanfromtags(article)

        doc_id = response.meta['doc_id']
        keyValueToUpdateDc = {"descriptionfull": article}

        self.update_valuesindatabase(doc_id, keyValueToUpdateDc)
