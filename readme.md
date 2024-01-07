===================================================

# PART-0: BASIC DEFINITIONS

===================================================  

PREFIXES USED IN THIS DOCUMENT:
>cmd>  - executing in Command Line  
>open> - just open file in editor  
>ss> - Scrapy Shell command  
>\> - just line of code

{ANYVARIABLE} - just interpolation for any variable inside of code

===================================================
SCRAPY MODULES DESCRIPTION:

work pipeline:
spider -> engine ->pipelines -> database

modules:
items.py - DTO - keeps data object for parsed items from source - serializing
pipelines.py - STANDARDIZATION - using for TRANSFORMING ITEMS FIELDS and data types using ItemAdapter and STORING data. Save parsing results into the DATABASE
middlewares.py - FAKE USER AGENTS

---------------------------------------------------

===================================================

# PART-1: CREATE PROJECT AND SETTING UP

===================================================  

### 0) New scrapy project creation
>cmd> scrapy startproject {SCRAPERNAME}

#current SCRAPERNAME is tradescraper. It includes spiders for different trade platforms

---------------------------------------------  

1) Spider creation for specific platform

>cmd> cd {PROJECTNAME}
>cmd> scrapy genspider {SPIDERNAME} {DOMAINPART}

# SPIDERNAME is just spider title
# DOMAINPART is a restricted domain part for specific spider

---------------------------------------------  

### 1) Configure settings inside the scrapy.cfg

>cmd>open> scrapy.cfg

```  
[settings]  
default = bookscraper.settings  
shell = ipython
```

#adding scrapy shell to project

>cmd>open> SCRAPERNAME/settings.py

```
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

#setting up option to ignore robots.txt restrictions and other settings

---------------------------------------------  

### 2) Using scrapy shell to complete research first portal example (cointelegraph.com) using browser dev tools

>cmd> cd tradescraper
>cmd> scrapy shell
>ss>
```
import json

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
        'length': 15,
        'offset': 0,
        'order': 'postPublishedTime',
        'short': 'en',
        'slug': 'bitcoin',
    },
}


fetch(url, headers=headers, body=json.dumps(params))
```

#it is important to encode "params" dictionary into string with using json.dumps to avoid TypeError on request
#fetch(..) - is procedure that returns into static variable "response" (available in context already) object Response type
#requested count of data and passed data offset can be regulated by values of keys: 'length' and 'offset' from "params" dictionary. All values equal to 0 == N % 15, where N is requested offset for this website

>ss>
```
response
```

#Out[..]: <200 https://conpletus.cointelegraph.com/v1/>
#checking in scrapy shell that we got correct response

>ss>
```
response.body
```

#Out[..]: b'{"data":{"locale":{"tag":{"cacheKey":"en.TagType.4"...etc
#look up in scrapy shell we see, that got response have body of document. Next we can start to construct the parser as is...

---------------------------------------------  

### 3.1) Research. Visualization document body

>ss>
```
with open("o.txt",'w', encoding='utf-8-sig') as fw:
    fw.write(str(response.body))
```

#save response document body into text document

>open> "o.txt"
>ctrl+c> copy saved body of response
>open> https://codebeautify.org/jsonviewer
>ctrl+v> paste saved copied body of response from "o.txt"

#make better visualization of document need to be parsed

---------------------------------------------  

### 3.2) Research. Setting up parser getters for specific values

>ss> j = json.loads(response.body.decode('utf-8-sig'))

#converting document body into dictionary object

>ss>
```
postsLst = j["data"]["locale"]["tag"]["posts"]["data"]
```

#select list of posts inside the dictionary

>ss>
```
p = postsLst[0]
```

#getting example post to lookup as a snippet

```
{'cacheKey': 'en.PostType.121854',
 'id': '121854',
 'slug': 'why-ethereum-major-gains-vs-bitcoin-new-year-s',
 'views': 4014,
 'postTranslate': {'cacheKey': 'en.PostTranslateType.840122',
  'id': '840122',
  'title': 'Has Ethereum finally bottomed vs. Bitcoin? ETH price technicals hint at gains',
  'avatar': 'https://s3.cointelegraph.com/uploads/2023-12/376ac544-7a52-4adf-badf-8baa86579970.jpg',
  'published': '2023-12-22T12:00:22+00:00',
  'publishedHumanFormat': 'Dec 22, 2023',
  'leadText': 'A rising wedge pattern is developing on Ether’s daily chart versus Bitcoin, increasing the likelihood of a breakout move by New Year’s.',
  'author': {'cacheKey': 'en.AuthorType.1261',
   'id': '1261',
   'slug': 'yashu-gola',
   'authorTranslates': [{'cacheKey': 'en.AuthorTranslateType.18284',
     'id': '18284',
     'name': 'Yashu Gola',
     '__typename': 'AuthorTranslate'}],
   '__typename': 'Author'},
  '__typename': 'PostTranslate'},
 'category': {'cacheKey': 'en.CategoryType.89',
  'id': '89',
  'slug': 'market-analysis',
  '__typename': 'Category'},
 'author': {'cacheKey': 'en.AuthorType.1261',
  'id': '1261',
  'slug': 'yashu-gola',
  'authorTranslates': [{'cacheKey': 'en.AuthorTranslateType.18284',
    'id': '18284',
    'name': 'Yashu Gola',
    '__typename': 'AuthorTranslate'}],
  '__typename': 'Author'},
 'postBadge': {'cacheKey': 'en.PostBadgeType.59',
  'id': '59',
  'label': 'info',
  'postBadgeTranslates': [{'cacheKey': 'en.PostBadgeTranslateType.1277',
    'id': '1277',
    'title': 'Market Analysis',
    '__typename': 'PostBadgeTranslate'}],
  '__typename': 'PostBadge'},
 'showShares': True,
 'showStats': True,
 '__typename': 'Post'}
```

#this is how may look every one snippet inside the postsLst

```
a = p["postTranslate"]

url = p["slug"]
datepost = a["published"]
category = p["postBadge"]["postBadgeTranslates"][0]["title"]

viewscount = p["views"]
title = a["title"]
author = p["author"]["authorTranslates"][0]["name"]
```

#setting up values need to be parsed

```
area = p.get("postTranslate")

d = {
    "url": f'https://cointelegraph.com/news/{str(p.get("slug")).strip()}',
    "datepost": str(area.get("published")),
    "category": str(p["postBadge"]["postBadgeTranslates"][0]["title"]),
    "viewscount": str(p.get("views")),
    "title": str(area.get("title")).strip(),
    "description": str(area.get("leadText")).strip(),
    "author": str(p["author"]["authorTranslates"][0]["name"])
}
```

#creation output dictionary

