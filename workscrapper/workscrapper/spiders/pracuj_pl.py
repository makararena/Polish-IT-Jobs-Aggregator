import scrapy
import datetime
from workscrapper.items import JobsItem

class JobSpider(scrapy.Spider):
    name = "pracuj_pl_spider"
    
    start_url_number = 1
    base_url = "https://it.pracuj.pl/praca?pn="
    upload_id = str(datetime.date.today()) + "_" + "pracuj_pl_spider"
    
    def start_requests(self):
        while self.start_url_number <= 200:  # Adjust the condition to control the number of pages
            start_url = f"{self.base_url}{self.start_url_number}"
            yield scrapy.Request(url=start_url, callback=self.parse)
            self.start_url_number += 1

    def parse(self, response):
        job_links = response.css('a.tiles_c8yvgfl.core_n194fgoq::attr(href)').getall()
        
        for job_link in job_links:
            yield scrapy.Request(url=job_link, callback=self.parse_job_details)

    def parse_job_details(self, response):
        item = JobsItem()
        item['job_title'] = response.css('h1[data-test="text-positionName"]::text').get() or 'N/A'
        item['employer_name'] = response.css('h2[data-test="text-employerName"]::text').get() or 'N/A'
        item['location'] = response.css('div[data-test="offer-badge-description"]::text').get() or 'N/A'
        item['expiration'] = response.css('li[data-test="sections-benefit-expiration"] div[data-test="offer-badge-description"]::text').get() or 'N/A'
        item['contract_type'] = response.css('li[data-test="sections-benefit-contracts"] div[data-test="offer-badge-title"]::text').get() or 'N/A'
        item['experience_level'] = response.css('li[data-test="sections-benefit-employment-type-name"] div[data-test="offer-badge-title"]::text').get() or 'N/A'    
        item['hybryd_full_remote'] = response.css('li[data-scroll-id="work-modes"] div[data-test="offer-badge-title"]::text').get() or 'N/A'


        salary_range = response.css('div[data-test="text-earningAmount"]::text').get()
        salary_range = salary_range.strip() if salary_range else 'N/A'
        
        salary_currency = response.css('div[data-test="text-earningAmount"] + div.c1d58j13::text').get()
        salary_currency = salary_currency.strip() if salary_currency else 'N/A'
        
        salary_type = response.css('div[data-test="text-earningAmount"] + div.sxxv7b6::text').get()
        salary_type = salary_type.strip() if salary_type else 'N/A'
        
        item['salary'] = f"{salary_range} {salary_currency} {salary_type}".strip()
        
        item['technologies'] = ';'.join([
            tech.strip()
            for tech in response.css('section[data-test="section-technologies"] ul[data-test="aggregate-open-dictionary-model"] li[data-test="item-technologies-expected"] p::text').getall()
        ]) or 'N/A'
        
        item['responsibilities'] = ';'.join([
            resp.strip()
            for resp in response.css('section[data-test="section-responsibilities"] li.tkzmjn3::text').getall()
        ]) or 'N/A'

        item['requirements'] = ';'.join([
            resp.strip()
            for resp in response.css('section[data-test="section-requirements"] li.tkzmjn3::text').getall()
        ]) or 'N/A'

        item['offering'] = ';'.join([
            resp.strip()
            for resp in response.css('section[data-test="section-offered"] li.tkzmjn3::text').getall()
        ]) or 'N/A'

        item['benefits'] = ';'.join([
            benefit.strip()
            for benefit in response.css('ul[data-test="list-benefits"] div[data-test="text-benefit-title"]::text').getall()
        ]) or 'N/A'
        
        item['url'] = str(response.url)
        item['date_posted'] = datetime.date.today()
        item['upload_id'] = self.upload_id
        
        yield item
    