# -*- coding: utf-8 -*-
from WebScraper import BaseClassWithWeakReferenceCount, WebScrapyMongoDataStorage

class TaobaoDotComCrawler(BaseClassWithWeakReferenceCount):

      mongo_uri = 'mongodb://localhost:27017',
      mongo_db = 'taobao_video_db'

      def __init__(self, webscrapy):
          super(self)
          self.dataStorage = WebScrapyMongoDataStorage() \
              .getDataStorageClient(self.mongo_uri, self.mongo_db)
          self.driver = webscrapy.driver

      pass

      #https://www.taobao.com/
      def parseTaobaoAllCategories(self, page):

          self.driver.get(page)

          taobaoCategories = list()

          categories = self.scrapy.parseElements([("ul.sub-nav li a", None)])

          if (categories == None):
              return

          for category in categories:

              item = {}

              item["link"] = category.get_attribute("href")
              item["name"] = category.text

              taobaoCategories.append(item)

          return (categories, "Taobao_Categories_Collection")
