import scrapy
from traderscraper.items import TraderscraperItem
from datetime import datetime

class CoinjournalSpider(scrapy.Spider):
    name = "coinjournal"
    allowed_domains = ["coinjournal.net"]
    start_urls = ["https://coinjournal.net/news/"]

    download_delay = 3#pause between requests

    maxcountofrequests = 5

    def parse(self, response):

        newsLst = response.css("div.article-card")

        if newsLst:

            ti = TraderscraperItem()

            for snippet in newsLst:
                ti["url"] = snippet.css("a").attrib["href"]
                datepost = snippet.css("a span.block::text, div.block span.block::text").get().strip()
                if datepost:
                    ti["datepost"] = datetime.strptime(datepost, "%d %B %Y").isoformat()
                ti["category"] = str(snippet.css("div.article-card__tag span.block::text").get())
                ti["viewscount"] = 0
                ti["title"] = str(snippet.css("h2 b::text, h2 a::text").get()).strip()
                ti["descriptionshort"] = str()
                ti["descriptionfull"] = str()
                ti["author"] = str()

                #refkey: URL: https://coinjournal.net/news/bitget-report-2023-remarkable-94-surge-in-spot-trading-accompanied-by-a-110-spike-in-bgb-volume/   ---> bitget-report-2023-remarkable-94-surge-in-spot-trading-accompanied-by-a-110-spike-in-bgb-volume
                ti["refkey"] = ti["url"].split('/')[-2]

                yield ti

        nexturl = response.css("li a.next")
        if not nexturl:
            return

        nexturl = nexturl.attrib["href"]
        if nexturl and self.maxcountofrequests > 0:
            self.maxcountofrequests -= 1
            yield response.follow(nexturl, callback=self.parse)