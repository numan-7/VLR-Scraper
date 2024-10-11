import os
import sys
import django
import logging

BOT_NAME = "spider"

SPIDER_MODULES = ["spider.spiders"]
NEWSPIDER_MODULE = "spider.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

ITEM_PIPELINES = {
    'spider.pipelines.SpiderPipeline': 300,
}

# Configure logging levels
LOG_LEVEL = 'WARNING'  

sys.path.append('/mnt/c/Users/Yor/Desktop/portfolio/vlr-webscraping')
os.environ['DJANGO_SETTINGS_MODULE'] = 'scraper.settings'
django.setup()

DOWNLOADER_MIDDLEWARES = {
    'spider.middlewares.ProxyMiddleware': 350,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}
