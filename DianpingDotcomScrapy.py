# -*- coding: utf-8 -*-
from WebScraper import BaseClassWithWeakReferenceCount, WebScrapyMongoDataStorage

class DianpingDotComCrawler(BaseClassWithWeakReferenceCount):

    mongo_uri = 'mongodb://localhost:27017',
    mongo_db = 'dianping_db'

    def __init__(self, webscrapy):
          super(self)
          self.dataStorage = WebScrapyMongoDataStorage()\
                       .getDataStorageClient(self.mongo_uri, self.mongo_db)
          self.driver = webscrapy.driver

    #http://www.dianping.com/shanghai
    def parseDianpingAllCategories(self, page):

        self.driver.get(page)

        dianpingCategories = list()

        categories = self.scrapy.parseElements([("div.cate-nav  a.index-title", None),
                                                ("div.sec-items  a.second-item", None)])

        if (categories == None):
            return

        for category in categories:

            dianpingItem = {}

            dianpingItem["link"] = category.get_attribute("href")
            dianpingItem["category"] = category.get_attribute("data-category")
            dianpingItem["name"] = category.text

            dianpingCategories.append(dianpingItem)


        return (categories, "Dianping_Categories_Collection")

    # "http://www.dianping.com/shop/110668222"
    def parseDianpingShopDetailPage(self, page):

        shopDetailObj = {}

        self.driver.get(page)

        shopDetailObj["title"] = self.scrapy.parseElements([("h1.shop-name", "text")])

        shopDetailObj["briefInfo"] = self.scrapy.parseElements([(".brief-info item", "text")])

        shopDetailObj["address"] =  self.scrapy.parseElements([(".address .item", "title")])

        shopDetailObj["tels"] = self.scrapy.parseElements([(".tel .item", "text")])

        shopDetailObj["otherInfo"] =  self.scrapy.parseElements([(".J-other .info .item", "text")])

        shopDetailObj["sales"] = self.scrapy.parseElements([("#sales .item", "text")])

        shopDetailObj["recommends"] = self.scrapy.parseElements([("#shop-tabs .shop-tab-recommend a.item", "title")])

        shopDetailObj["official_albums"] = self.scrapy.parseElements([(".shop-tab-photos .item a", "href")])

        shopDetailObj["official_photos"] = self.scrapy.parseElements([(".shop-tab-photos .item", "href")])

        return (shopDetailObj, "Dianping_Shops_Collection")


    #  "http://www.dianping.com/shanghai/ch30/g141"
    def parseDianpingShopListPage(self, page, isNeedParse = True):

        self.driver.get(page)

        dianpingSubPage = {}

        dianpingSubPage["subcategory"] = self.scrapy.parseElements([(".bread span:last-child span", "text")])

        dianpingSubPage["currentPage"] = self.scrapy.parseElements([(".page .cur", "text")])

        shopDetailsPageUrls = self.scrapy.parseElements([("#shop-all-list li .pic a", "href")])

        if isNeedParse == True:

            allPageIndexLinks = self.scrapy.parseElements([(".page  a:nth-last-child(2)", "data-ga-page")])

            print(len(allPageIndexLinks))

            totalPageCount = allPageIndexLinks[0].get_attribute("data-ga-page")

            print(totalPageCount)

            for pn in range(2, int(totalPageCount) + 1):

                nextPage = page + 'p{}'.format(pn)

                nextPageOfShopSet = self.parseDianpingShopListPage(nextPage, False)[0]

                for shopDetailsPage in nextPageOfShopSet:
                    shopDetailsPageUrls.append(shopDetailsPage)

            return (shopDetailsPageUrls, "Dianping_Shop_Links_Collection")

        else:
            return (shopDetailsPageUrls, "Dianping_Shop_Links_Collection")


    def __del__(self):
        pass


if __name__ == '__main__':

    dianpingDotComCrawler = DianpingDotComCrawler()

    dianpingMainPageUri = "http://www.dianping.com/shanghai"

    dianpingMainPageObjPair = dianpingDotComCrawler.parseDianpingAllCategories(dianpingMainPageUri)

    dianpingDotComCrawler.dataStorage.saveOneToStorage(dianpingMainPageObjPair)






