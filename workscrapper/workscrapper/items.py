# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
class JobsItem(scrapy.Item):
    job_title = scrapy.Field()
    employer_name = scrapy.Field()
    location = scrapy.Field()
    hybryd_full_remote = scrapy.Field()
    expiration = scrapy.Field()
    contract_type = scrapy.Field()
    experience_level = scrapy.Field()
    salary = scrapy.Field()
    technologies = scrapy.Field()
    responsibilities = scrapy.Field()
    requirements = scrapy.Field()
    offering = scrapy.Field()
    benefits = scrapy.Field()
    url = scrapy.Field()
    date_posted = scrapy.Field()
    upload_id = scrapy.Field()
