from scrapy import cmdline
#cmdline.execute("scrapy crawl cointelegraphspider -O cointelegraphspider.csv".split())#scrape with creating new file output
#cmdline.execute("scrapy crawl cointelegraphspider -o cointelegraphspider.csv".split())#scrape with appending already exists file output -o
#cmdline.execute("scrapy crawl cointelegraphspider".split())#scrape into database

cmdline.execute("scrapy crawl coinjournal".split())#scrape into database