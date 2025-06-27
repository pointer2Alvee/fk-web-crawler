import scrapy
from scrapy.linkextractors import LinkExtractor
from datetime import datetime, timezone
from .book_schema import Book
from pydantic import ValidationError


from .mongodb_client import insert_to_db 

class CrawlingSpider(scrapy.Spider):
    name = "fkcrawler"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    
    def parse(self, response):
        books = response.css('article.product_pod')
        
        for book in books[:1]: # NOTE:- for testing -  books[:2]
            relative_url = book.css('h3 a ::attr(href)').get()

            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            
            yield response.follow(book_url, callback=self.parse_book)

        
        # pagination : continues visiting pages one after another
        # NOTE:- for testing - comment all  
        next_page = response.css('li.next a ::attr(href)').get()
        #page_number = int(next_page[-1][-6]) # ['catalogue/page-2.html'], [-1][-6] extracts '2' NOTE :- for testing
        
        # if next_page is not None :
        #     if 'catalogue/' in next_page:
        #         next_page_url = 'https://books.toscrape.com/' + next_page
        #     else:
        #         next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            
        #     yield response.follow(next_page_url, callback=self.parse)

    
    def parse_book(self, response):
        """
        scrapes/extracts individual book details from website
        """
        # ** Handled Unexpected Content Structures
        book_name = response.xpath("//div[@class='col-sm-6 product_main']/h1/text()").get()
        book_description = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_category = response.xpath('//div[@class="page_inner"]/ul/li[3]/a/text()').get()
        book_price_with_tax = response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Price (incl. tax)")]/following-sibling::td/text()').get()
        book_price_without_tax = response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Price (excl. tax)")]/following-sibling::td/text()').get()
        availability_text = response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Availability")]/following-sibling::td/text()').get()
        book_review = response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Number of reviews")]/following-sibling::td/text()').get()
        cover_image = response.xpath("//div[@class='item active']/img/@src").get()
        rating_class = response.xpath('//p[contains(@class, "star-rating")]/@class').get()

        # Safe parsing for tricky fields // # ** Handled Unexpected Content Structures
        book_availability = availability_text.split()[-2][1:] if availability_text and len(availability_text.split()) >= 2 else None
        book_rating = rating_class.split()[-1] if rating_class else None
        book_cover_image_url = response.urljoin(cover_image) if cover_image else None
        
        # Converting Necessary fields to numerics -  problem happens in mongodb_clinet.py --> combined = "|".join(key_fields) -- SOLVED 
        book_price_with_tax = float(book_price_without_tax.replace('£', '').strip())
        book_price_without_tax = float(book_price_without_tax.replace('£', '').strip())

        # Map text to number
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        book_rating = rating_map.get(book_rating, None)  # Returns None if not found
        book_review = int(book_review) if book_review and book_review.isdigit() else None
        
        # generator to scrape data # Final safe item
        status = "" # Scraped book Status
        if not all([book_name or book_description or book_category or book_price_with_tax or book_price_without_tax 
                or availability_text or book_review or cover_image or rating_class]):
            status = "partial-error" # If any one of the field is missing status = error
        else:
            status = "success"
        # Consctructs the data  
        book_data = {
            # Scraping individual book's data
            "book_name": book_name,
            "book_description": book_description,
            "book_category": book_category,
            "book_price_with_tax": book_price_with_tax,
            "book_price_without_tax": book_price_without_tax,
            "book_availability": book_availability,
            "book_review": book_review,
            "book_cover_image_url": book_cover_image_url,
            "book_rating": book_rating,
            
            # ** For storing metadata
            "crawl_timestamp": datetime.now(timezone.utc).isoformat(),
            "source_url": response.url,
            "status": status,
            
            # ** raw HTML snapshot
            "raw_html": response.text
        }
        
        # Insert to MongoDb
        # insert_to_db(**book_data)
        
        # Yield for Scrapy pipeline/logging
        #yield book_data
        

        # Validate with Pydantic before inserting
        try:
            book = Book(**book_data)
            insert_to_db(**book.model_dump())  
            #yield book.model_dump()
        except ValidationError as e:
            self.logger.warning(f"Validation failed for {response.url}: {e}")
        
        
                