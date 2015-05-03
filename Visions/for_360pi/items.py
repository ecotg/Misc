# -*- coding: utf-8 -*-
# Define here the models for your scraped items
import scrapy
from scrapy.contrib.loader.processor import TakeFirst, Compose


def utf_encode(val):
    return val.encode('utf-8')


class VisionsProduct(scrapy.Item):
    """
    Product container for scraped data from visions.ca.
    Each item in the container is encoded in utf-8 format
    before being outputted/written to JSON.
    """
    category = scrapy.Field(output_processor= Compose(TakeFirst(), utf_encode),
                            stop_on_none = False)
    product = scrapy.Field(output_processor = Compose(TakeFirst(), utf_encode),
                           stop_on_none = False)
    price = scrapy.Field(output_processor = Compose(TakeFirst(), utf_encode),
                         stop_on_none = False)
    availability = scrapy.Field(output_processor = TakeFirst())
