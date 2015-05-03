"""
Scrape: Visions.ca

To run this script, in this directory, run 'scrapy crawl visions' in the
terminal.

For each category listed on the lefthand banner on the
http://www.visions.ca/Default.aspx page, this script will extract the
product details for one product.

First, the spider will extract and follow the hrefs for all thirteen
categories, see rule 1. Then for all the categories, apart from 'Bundles',
the spider will find and follow href link for the first brand listed on the
category pages' left hand menu, see rule 2. Once on the brand page, this
spider will extract the details for the first product listed on that page.

For the 'Bundles' category, due to the category page's different layout,
the spider will extract the link for the first product listed on that page,
follow that link, and then extract the product's details, see Rule 3.

For each run of the spider, a JSON file and log file are created, containing
the thirteen scraped products, one per category, and a log for the spider,
respectively. Each of thirteen categories are listed as a field for their
respective product.

Script utilizes the Scrapy method, its xpath, ItemLoader and LinkExtractor
classes to obtain the product data.


"""

from for_360pi.items import VisionsProduct
from scrapy.selector import Selector
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor


class VisionSpyder(CrawlSpider):
    name = 'visions'
    allowed_domains = ['visions.ca']
    start_urls = ['http://www.visions.ca/Default.aspx']

    # Store long xpaths as a string to aid clarity.
    xpath1 = ('//*[@id="mastermenu-container"]/ul[@id="mastermenu-startbtn"]'
              '/li/ul[@id="mastermenu-dropdown"]/li/a[starts-with(@href,'
              '"/Catalogue/")]')

    xpath2 = ('//*[@id="subcatemenu-container"]'
              '/div[@id="subcatemenu-brand-all"]/ul/li[1]')

    xpath3 = ('//*[@id="ctl00_tdMainPanel"]/div[contains(@class,'
              '"bundleItem")][1]//a[contains(@id, "BundleName")]')

    rules = (Rule(LinkExtractor(allow = ('/Catalogue/.*'),
                                restrict_xpaths = (xpath1),
                                deny_domains = ('ProductResults')),),
             Rule(LinkExtractor(restrict_xpaths = (xpath2)),
                  callback = 'parse_by_brand'),
             Rule(LinkExtractor(restrict_xpaths = (xpath3)),
                  callback = 'parse_by_product'),)

    def parse_by_brand(self, response):
        """
        Except for the 'Bundles' page, for the first brand listed on each
        category page, extract the product details for the first listed
        product.
        """

        selector = Selector(response)

        # Use the 'Bread Crumbs' attribute to compose the category path.
        self.crumb_xpath_1 = ('//*[@id="ctl00_pnlBreadCrumbs"]/a//text()')
        self.crumb_1 = selector.xpath(self.crumb_xpath_1).extract()
        self.crumb_xpath_2 = ('//*[@id="ctl00_pnlBreadCrumbs"]/span//text()')
        self.crumb_2 = selector.xpath(self.crumb_xpath_2).extract()
        self.category = ('/'.join(self.crumb_1).encode('utf-8') + '/' +
                         '/'.join(self.crumb_2).encode('utf-8'))

        self.empty_page_xpath = ('//*[@id="ctl00_tdMainPanel"]'
                                 '/div/div[@id="ctl00_Content'
                                 'PlaceHolder1_pnlNoRecords"]')

        if (selector.xpath(self.empty_page_xpath)):
            loader = ItemLoader(item = VisionsProduct(), response = response)

            self.empty_page = 'Empty Page/No Records'

            # set product details for an empty page
            loader.add_value('category', self.category)
            loader.add_value('product', self.empty_page)
            loader.add_value('price', self.empty_page)
            loader.add_value('availability', self.empty_page)

        else:
            # If not-empty, extract and load product details

            self.results_xpath = ('//*[contains(@class,'
                                  '"productresult-itembox")]')
            self.results = selector.xpath(self.results_xpath)
            loader = ItemLoader(item = VisionsProduct(),
                                selector = self.results[0])

            # Store long xpaths in dict to aid clarity
            self.field_xpaths = {
                'product': ('div[contains(@class,'
                            '"contentright")]/h2/a/font/text()'),
                'price': ('div[contains(@class, "contentright")]'
                          '/div/div/span[@class="price"]'),
                'price_gif': ('div[contains(@class,"contentright")'
                              ']/div/div[contains(@id, "AddToCart")]/a/img'),
                'clearance_gif': ('div[contains(@class,'
                                  '"productresult-imagebox")]/div/div[contains'
                                  '(@style,"position:absolute; bottom")]/img'
                                  '[contains(@src, "final_clearance_'
                                  'box.gif")]')
            }

            loader.add_value('category', self.category)
            loader.add_xpath('product', self.field_xpaths['product'])

            # Use the first listed price, which equals the sale price if
            # product on sale, else is the regular price.
            # For products without listed price, check for 'In Store' img
            # attribute to indicate price detail.
            try:
                loader.add_xpath('price', self.field_xpaths['price'],
                                 re = '\$[\d]*[,]*[\d]*\.[\d]*')
            except IndexError:
                if (self.results[0].xpath(self.field_xpaths['price_gif'])):
                    loader.add_value('price', 'Available only In-Store')

            # Use the Final clearance gif to help determine product
            # availability.
            if (self.results[0].xpath(self.field_xpaths['clearance_gif'])):
                loader.add_value('availability', 'Limited Quantity/Clearance')
            else:
                loader.add_value('availability', 'Not Limited/Clearance Item')

        yield loader.load_item()

    def parse_by_product(self, response):
        """
        For the 'Bundles' category, grab the product details for the first
        product listed.
        """
        self.selector = Selector(response)
        self.results = self.selector.xpath('//*[@id="ctl00_tdMainPanel"]')
        loader = ItemLoader(item = VisionsProduct(),
                            selector = self.results[0])

        self.field_xpaths = {
            'product': ('div[contains(@class, "catalogueTitle")]'
                        '/h3/text()'),
            'price': ('div[@id="ctl00_ContentPlaceHolder1_pnl'
                      'Bundle"]/div[@id="divProductDetails"]/div'
                      '[contains(@class, "priceAddToCart")]/div[1]/span'
                      '[contains(@id, "SalePrice")]/text()')
        }

        # Extract and load product details
        loader.add_xpath('product', self.field_xpaths['product'])
        loader.add_xpath('price', self.field_xpaths['price'],
                         re = '\$[\d]*[,]*[\d]*\.[\d]*')
        loader.add_value('availability', 'Not Limited/Clearance Item')

        # Because it's an individual product page, manually set the category
        self.category = '/'.join(['Home', response.url.split('/')[4]])
        loader.add_value('category', self.category)

        yield loader.load_item()


def main():
    VisionSpyder()

if __name__ == '__main__':
    main()