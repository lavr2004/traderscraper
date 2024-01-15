from selenium import webdriver
from scrapy.http import HtmlResponse

class CustomSeleniumMiddleware:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            driver_path=crawler.settings.get('SELENIUM_DRIVER_EXECUTABLE_PATH')
        )

    def process_request(self, request, spider):
        if not self.driver:
            self.driver = webdriver.Chrome()
            spider.log(f'Selenium WebDriver initialized for {spider.name}.')

        self.driver.get(request.url)
        body = self.driver.page_source
        return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

    def spider_closed(self, spider):
        if self.driver:
            self.driver.quit()
            spider.log(f'Selenium WebDriver closed for {spider.name}.')

    def process_exception(self, request, exception, spider):
        # Обработка исключений
        pass
