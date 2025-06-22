import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class CrawlingSpider(scrapy.Spider):
    name = "fkcrawler"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css('article.product_pod')
        
        for book in books:
            relative_url = book.css('h3 a ::attr(href)').get()

            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            
            yield response.follow(book_url, callback=self.parse_book)

        # pagination : continues visiting pages one after another 
        next_page = response.css('li.next a ::attr(href)').get()
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            
            yield response.follow(next_page_url, callback=self.parse)


    
    
    def parse_book(self, response):
        """
        scrapes each book/item details
        """
        books = response.xpath('//article[@class="product_pod"]')
        
        # generator to scrape data
        yield {
            "book_name" : response.xpath("//div[@class='col-sm-6 product_main']/h1/text()").get(),
            "book_description" : response.xpath("//div[@id=product_description]/following-sibling::p/text()").get(),
            "book_category" : response.xpath('//div[@class="page_inner"]/ul/li[3]/a/text()').get(),
            "book_price_with_tax" : response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Price (incl. tax)")]/following-sibling::td/text()').get(),
            "book_price_without_tax" : response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Price (excl. tax)")]/following-sibling::td/text()').get(),
            "book_availability" : response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Availability")]/following-sibling::td/text()').get().split()[-3],
            "book_review" : response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Number of reviews")]/following-sibling::td/text()').get(),
            "book_cover_image_url" : response.xpath("//div[@class='item active']/img/@src").get(),
            "book_rating" : response.xpath('//p[contains(@class, "star-rating")]/@class').get().split()[-1],
            
        }