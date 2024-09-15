import scrapy
from datetime import datetime, timedelta
from workscrapper.items import JobsItem

class JobSpider(scrapy.Spider):
    name = "theprotocol_spider"
    start_url_number = 1
    base_url = "https://theprotocol.it/praca?pageNumber="
    upload_id = str(datetime.today() - timedelta(days=1)) + "_" + "theprotocol_spider"
    
    def start_requests(self):
        while self.start_url_number <= 10:
            start_url = f"{self.base_url}{self.start_url_number}"
            yield scrapy.Request(url=start_url, callback=self.parse)
            self.start_url_number += 1
            
    def parse(self, response):
        job_links = response.css('a[data-test="list-item-offer"]::attr(href)').getall()
    
        for job_link in job_links:
            job_link = "https://theprotocol.it" + job_link
            yield scrapy.Request(url=job_link, callback=self.parse_job_details)
                
    def parse_job_details(self, response):
        item = JobsItem()

        item['job_title'] = response.css('h1[data-test="text-offerTitle"]::text').get() or 'N/A'
        item['employer_name'] = response.css('a[data-test="anchor-company-link"]::text').get() or 'N/A'
        item['location'] = response.css('div[data-test="text-workplaceAddress"]::text').get() or 'N/A'
        item['expiration'] = response.css('div[data-test="text-expirationDate"]::text').get() or 'N/A'
        item['contract_type'] = response.css('p[data-test="text-contractName"]::text').get() or 'N/A'
        item['experience_level'] = response.css('div[data-test="section-positionLevels"] div.tieu7dq.g1cobuf9 div.l1bcjc6p div.r4179ok.bldcnq5.ihmj1ec::text').getall() or 'N/A'   
        item['hybryd_full_remote'] = response.css('div[data-test="section-workModes"] div.r4179ok.bldcnq5.ihmj1ec::text').get() or 'N/A'
        salary = response.css('p[data-test="text-contractSalary"]::text').getall()
        salary = ' '.join(salary).strip()
        units = response.css('p[data-test="text-contractUnits"]::text').getall()
        units = ' '.join(units).strip()
        salary_type = response.css('p[data-test="text-contractUnits"]::text').get()
        salary_type = salary_type.strip() if salary_type else 'N/A'

        item['salary'] = f"{salary} {salary_type}".strip()
        
        item['technologies'] = ';'.join([
            tech.strip()
            for tech in response.css('div[data-test="chip-technology"] span::text').getall()
        ]) or 'N/A'
        
        item['responsibilities'] = ';'.join([
            resp.strip()
            for resp in response.css('div[data-test="section-responsibilities"] *::text').getall()
        ]) or 'N/A'

        item['requirements'] = ';'.join([
            resp.strip()
            for resp in response.css('div[data-test="section-requirements"] *::text').getall()
        ]) or 'N/A'

        item['offering'] = ';'.join([
            resp.strip()
            for resp in response.css('div[data-test="section-offered"] ul.l1b2shk9 li.l1s7r86q div.r4179ok.bldcnq5.ihmj1ec::text').getall()
        ]) or 'N/A'

        item['benefits'] = ';'.join([
            benefit.strip()
            for benefit in response.css('div[data-test="section-training-space"] ul.l1b2shk9 li.l1s7r86q div.r4179ok.bldcnq5.ihmj1ec::text').getall() + \
                response.css('div[data-test="section-benefits"] ul.l1b2shk9 li.l1s7r86q div.r4179ok.bldcnq5.ihmj1ec::text').getall()

        ]) or 'N/A'
        
        item['url'] = str(response.url)
        item['date_posted'] = (datetime.today() - timedelta(days=1)).date()
        item['upload_id'] = self.upload_id
        
        yield item