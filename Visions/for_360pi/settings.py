# -*- coding: utf-8 -*-

# Scrapy settings for for_360pi project
from datetime import datetime
import os

BOT_NAME = 'for_360pi'

SPIDER_MODULES = ['for_360pi.spiders']
NEWSPIDER_MODULE = 'for_360pi.spiders'
LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
timestmp = datetime.now().strftime('%Y-%b-%d:%I-%M-%p')
LOG_FILE = os.getcwd() + '/LOGS/' + BOT_NAME + '-' + timestmp + '.log'

# Export results, as a json feed, to file
FEED_DIR = '/'.join(os.getcwd().split('/')[:-1]) + '/spiders/FEEDS'
FEED_URI = 'file:///' + FEED_DIR + '/%(name)s' + '/' + timestmp + '.json'
FEED_FORMAT = 'json'

FEED_EXPORTERS = {
     'json': 'scrapy.contrib.exporter.JsonItemExporter',
}


