import scrapy
from datetime import datetime, timezone
from pydantic import ValidationError

from .book_schema import Book   # pydantic validation
from .mongodb_client import insert_to_db # insert to mongodb

class CrawlingSpider(scrapy.Spider):
    """
    Class for crawling website, scraping and pushing scraped data to mongodb
    """
    
    # Crawler's name
    name = "fkcrawler"
    
    # Allowed domains, can't crawl on other domains except listed ones
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    
    # Parses all pages 
    def parse(self, response):
        """
        Parse the main listing page of 'books.toscrape.com' to extract individual book URLs 
        and follow pagination links.

        This method performs the following tasks:
        - Extracts book links from the current page.
        - Constructs full URLs and yields requests to `parse_book` for each individual book.
        - Identifies the "Next" page link and recursively yields a request to continue crawling subsequent pages.

        Parameters:
            response (scrapy.http.Response): The HTTP response object for the current listing page.

        Yields:
            scrapy.Request: A request to the individual book detail page handled by `parse_book`.
            scrapy.Request: A request to the next pagination page handled recursively by `parse`.
        """
        
        books = response.css('article.product_pod')
        
        # Extracts all book's url in the current page
        for book in books[:1]: # NOTE:- for testing -  books[:1]
            relative_url = book.css('h3 a ::attr(href)').get()
            
            # Some book_url have 'catalogue/' & some don't
            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            
            # Sends individual book's url to parse_book() func
            yield response.follow(book_url, callback=self.parse_book) 

        
        # Pagination : visits pages one after another | NOTE:- for testing - comment all  
        next_page = response.css('li.next a ::attr(href)').get()   
        if next_page is not None :
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            
            # Recursive call to this function with the next page's url
            yield response.follow(next_page_url, callback=self.parse)

    
    # Parses individual book's data from 'book_url'
    def parse_book(self, response):
        """
        Parses and extracts detailed information from an individual book's page.

        This method is responsible for:
        - Extracting book metadata (name, price, category, availability, rating, reviews).
        - Handling edge cases such as missing or malformed data.
        - Cleaning and converting specific fields into proper types (e.g., float, int).
        - Validating extracted data using a Pydantic model (`Book`).
        - Inserting validated data into MongoDB via `insert_to_db`.
        - Logging a warning if validation fails.

        Parameters:
            response (scrapy.http.Response): The HTTP response from an individual book's page.

        Yields:
            None. (Data is inserted directly to MongoDB after validation)
        
        Logs:
            - Validation failures
        """
        
        # Scrapes required fields from book_url / ** --> Handled Unexpected Content Structures
        book_name = response.xpath("//div[@class='col-sm-6 product_main']/h1/text()").get()
        book_description = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_category = response.xpath('//div[@class="page_inner"]/ul/li[3]/a/text()').get()
        book_price_with_tax = response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Price (incl. tax)")]/following-sibling::td/text()').get()
        book_price_without_tax = response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Price (excl. tax)")]/following-sibling::td/text()').get()
        availability_text = response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Availability")]/following-sibling::td/text()').get()
        book_review = response.xpath('//table[@class="table table-striped"]//th[contains(text(), "Number of reviews")]/following-sibling::td/text()').get()
        cover_image = response.xpath("//div[@class='item active']/img/@src").get()
        rating_class = response.xpath('//p[contains(@class, "star-rating")]/@class').get()

        # Safe parse for tricky fields
        book_availability = availability_text.split()[-2][1:] if availability_text and len(availability_text.split()) >= 2 else None
        book_rating = rating_class.split()[-1] if rating_class else None
        book_cover_image_url = response.urljoin(cover_image) if cover_image else None
        
        # Converts some numeric fields to numerical values (float/int) - problem happens in mongodb_client.py --> combined = "|".join(key_fields) -- SOLVED 
        book_price_with_tax = float(book_price_without_tax.replace('£', '').strip())
        book_price_without_tax = float(book_price_without_tax.replace('£', '').strip())
        rating_map = { "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5 } # Map numerical text to actual number
        book_rating = rating_map.get(book_rating, None) 
        book_review = int(book_review) if book_review and book_review.isdigit() else None
        
        # Scraped book Status
        status = "" 
        
        # If any of the fields is missing, status = partial/error else "success"
        if not all([book_name or book_description or book_category or book_price_with_tax or book_price_without_tax or availability_text or book_review or cover_image or rating_class]):
            status = "partial-error" 
        else:
            status = "success"
            
        # Constructs book data  
        book_data = {
            # Scrapes individual book's data
            "book_name": book_name,
            "book_description": book_description,
            "book_category": book_category,
            "book_price_with_tax": book_price_with_tax,
            "book_price_without_tax": book_price_without_tax,
            "book_availability": book_availability,
            "book_review": book_review,
            "book_cover_image_url": book_cover_image_url,
            "book_rating": book_rating,
            
            # ** --> Store individual book's metadata
            "crawl_timestamp": datetime.now(timezone.utc).isoformat(),
            "source_url": response.url,
            "status": status,
            
            # ** --> Store raw HTML snapshot
            "raw_html": response.text
        }
        
        
        # Insert to MongoDb
        # insert_to_db(**book_data)
        
        # Yield for Scrapy pipeline/logging
        #yield book_data
        
        # Validate with Pydantic before inserting
        try:
            book = Book(**book_data)            # Pydantic Validation
            insert_to_db(**book.model_dump())   # Insert to mongoDB
             
            # Shows in terminal
            #yield book.model_dump() 
            
        except ValidationError as e:
            self.logger.warning(f"Validation failed for {response.url}: {e}")
        
        
                