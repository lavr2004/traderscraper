import scrapy
from traderscraper.items import TraderscraperItem
import time

class BitcoinmagazinecomSpider(scrapy.Spider):
    name = "bitcoinmagazinecom"

    allowed_domains = ["bitcoinmagazine.com"]
    start_urls = ["https://bitcoinmagazine.com"]

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'traderscraper.selenium_middleware.CustomSeleniumMiddleware': 800,
        },
    }

    #ClosingSpiderOnEvent - flag used in pipelines to invoke close spider if first doublicate found
    close_down = False

    def start_requests(self):
        yield scrapy.Request("https://bitcoinmagazine.com/articles", callback=self.parse)

    def parse(self, response):
        time.sleep(3)

        newslist = response.css("div.l-grid--item")

        if newslist:
            for n in newslist:
                # ClosingSpiderOnEvent - closing spider if flag is setting up (in pipelines)
                if self.close_down:
                    break

                ti = TraderscraperItem()

                ti["title"] = n.css("h2.m-card--header-text::text").get().strip()
                ti["url"] = "https://bitcoinmagazine.com" + n.css('a[phx-track-id="Title"]::attr(href)').extract_first()
                ti["datepost"] = n.css('time::attr(datetime)').get()
                ti["category"] = n.css('a[phx-track-id="Label"]::text').get()
                ti["viewscount"] = 0
                ti["descriptionshort"] = n.css("p.m-card--body::text").get()
                ti["descriptionfull"] = ""
                author = str(n.css('a[phx-track-id="SectionKey"]::text').get())
                ti["author"] = author.replace("By ", "").strip() if author.startswith("By ") else author

                ti["refkey"] = ti["url"].split('/')[-1]

                yield ti