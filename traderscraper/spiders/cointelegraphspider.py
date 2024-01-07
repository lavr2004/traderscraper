import scrapy
import requests
import json


class CointelegraphspiderSpider(scrapy.Spider):
    name = "cointelegraphspider"
    allowed_domains = ["cointelegraph.com", "conpletus.cointelegraph.com"]
    start_urls = ["https://cointelegraph.com/tags/bitcoin"]

    toRequestCountSnippets = 15#count of snippets to request is must being modular to (15)

    def start_requests(self):
        url = 'https://conpletus.cointelegraph.com/v1/'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'utf-8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers',
        }
        params = {
            'operationName': 'TagPageQuery',
            'query': 'query TagPageQuery($short: String, $slug: String!, $order: String, $offset: Int!, $length: Int!) {\n  locale(short: $short) {\n    tag(slug: $slug) {\n      cacheKey\n      id\n      slug\n      avatar\n      createdAt\n      updatedAt\n      redirectRelativeUrl\n      alternates {\n        cacheKey\n        short\n        domain\n        id\n        code\n        __typename\n      }\n      tagTranslates {\n        cacheKey\n        id\n        title\n        metaTitle\n        pageTitle\n        description\n        metaDescription\n        keywords\n        __typename\n      }\n      posts(order: $order, offset: $offset, length: $length) {\n        data {\n          cacheKey\n          id\n          slug\n          views\n          postTranslate {\n            cacheKey\n            id\n            title\n            avatar\n            published\n            publishedHumanFormat\n            leadText\n            author {\n              cacheKey\n              id\n              slug\n              authorTranslates {\n                cacheKey\n                id\n                name\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          category {\n            cacheKey\n            id\n            slug\n            __typename\n          }\n          author {\n            cacheKey\n            id\n            slug\n            authorTranslates {\n              cacheKey\n              id\n              name\n              __typename\n            }\n            __typename\n          }\n          postBadge {\n            cacheKey\n            id\n            label\n            postBadgeTranslates {\n              cacheKey\n              id\n              title\n              __typename\n            }\n            __typename\n          }\n          showShares\n          showStats\n          __typename\n        }\n        postsCount\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}',
            'variables': {
                'cacheTimeInMS': 300000,
                'length': self.toRequestCountSnippets,
                'offset': 0,
                'order': 'postPublishedTime',
                'short': 'en',
                'slug': 'bitcoin',
            },
        }
        yield scrapy.FormRequest(url=url, method='POST', headers=headers, body=json.dumps(params), callback=self.parse)
        #yield scrapy.Request(url=self.start_urls[0], callback=self.parse)

    def parse(self, response):
        j = json.loads(response.body.decode('utf-8-sig'))

        postsLst = j["data"]["locale"]["tag"]["posts"]["data"]
        assert len(postsLst), f"ER - didnt find posts on request {response.url} by attributes {response.attributes} "

        for p in postsLst:
            area = p.get("postTranslate")

            yield {
                "url": f'https://cointelegraph.com/news/{str(p.get("slug")).strip()}',
                "datepost": str(area.get("published")),
                "category": str(p["postBadge"]["postBadgeTranslates"][0]["title"]),
                "viewscount": str(p.get("views")),
                "title": str(area.get("title")).strip(),
                "description": str(area.get("leadText")).strip(),
                "author": str(p["author"]["authorTranslates"][0]["name"])
            }