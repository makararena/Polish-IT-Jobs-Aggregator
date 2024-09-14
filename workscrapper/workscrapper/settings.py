BOT_NAME = "workscrapper"

SPIDER_MODULES = ["workscrapper.spiders"]
NEWSPIDER_MODULE = "workscrapper.spiders"


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 20


DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

ITEM_PIPELINES = {
    'workscrapper.pipelines.PostgreSQLPipeline': 1,
}

AUTOTHROTTLE_ENABLED = True

LOG_LEVEL="INFO"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
TELNETCONSOLE_ENABLED = False
