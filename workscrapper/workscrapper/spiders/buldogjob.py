import scrapy
from datetime import datetime, timedelta
from workscrapper.items import JobsItem

class JobSpider(scrapy.Spider):
    name = "buldogjob_spider"
    
    start_url_number = 1
    base_url = "https://bulldogjob.pl/companies/jobs/s/page,"
    upload_id = str(datetime.today() - timedelta(days=1)) + "_" + "buldogjob_spider"
    
    def start_requests(self):
        while self.start_url_number <= 5:
            start_url = f"{self.base_url}{self.start_url_number}"
            yield scrapy.Request(url=start_url, callback=self.parse)
            self.start_url_number += 1

    def parse(self, response):
        job_links = response.css('a.JobListItem_item__M79JI::attr(href)').getall()
        
        for job_link in job_links:
            yield scrapy.Request(url=job_link, callback=self.parse_job_details)
            
    def parse_job_details(self, response):
        item = JobsItem() 
        
        item['job_title'] = response.css('aside div p.font-medium.text-3xl::text').get() or 'N/A'
        
        item['employer_name'] = response.css('aside div p.mb-1::text').get() or 'N/A'
        
        all_texts = response.css('p.text-md.xl\\:text-c22.leading-6::text').getall()
        item['location'] = all_texts[4:] if len(all_texts) > 4 else 'N/A'
        item['expiration'] = all_texts[0] if len(all_texts) > 0 else 'N/A'
        item['contract_type'] = all_texts[3] if len(all_texts) > 3 else 'N/A'
        item['experience_level'] = all_texts[1] if len(all_texts) > 1 else 'N/A'
        item['hybryd_full_remote'] = 'N/A'

        salaries = []
        salary_details = response.css('aside div.mb-4')
        for detail in salary_details:
            salary_amount = detail.css('p.text-c22.xl\\:text-2xl::text').get()
            salary_amount = salary_amount.strip() if salary_amount else 'N/A'
            
            salary_type = detail.css('p.text-gray-300.xl\\:text-c22.font-normal.mt-1::text').get()
            salary_type = salary_type.strip() if salary_type else 'N/A'
            
            full_salary_info = f"{salary_amount} ({salary_type})"
            salaries.append(full_salary_info)
        
        item['salary'] = ' / '.join(salaries) if salaries else 'N/A'
        
        item['technologies'] = 'N/A'
        
        item['responsibilities'] = ';'.join([
            resp.strip()
            for resp in response.css('section#1-panel div.content.list--check ul li::text').getall()
        ]) or 'N/A'

        item['requirements'] = ';'.join([
            req.strip()
            for req in response.css('section#3-panel div.content.list--check ul li::text').getall()
        ]) or 'N/A'

        item['offering'] = ';'.join([
            offer.strip()
            for offer in response.css('section#2-panel div.content.list--check ul li::text').getall()
        ]) or 'N/A'

        item['benefits'] = ';'.join([
            benefit.strip()
            for benefit in response.css('ul.BenefitsList_benefits__data__fDPbB li::text').getall()
        ]) or 'N/A'
        
        # Set URL, date posted, and upload ID
        item['url'] = response.url
        item['date_posted'] = (datetime.today() - timedelta(days=1)).date()
        item['upload_id'] = self.upload_id
        
        yield item