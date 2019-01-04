# -*- coding: utf-8 -*-
from WebScraper import BaseClassWithWeakReferenceCount, WebScrapyMongoDataStorage

class BilibiliDotComCrawler(BaseClassWithWeakReferenceCount):

      mongo_uri = 'mongodb://localhost:27017',
      mongo_db = 'bilibili_video_db'

      def __init__(self, webscrapy):
          super(self)
          self.dataStorage = WebScrapyMongoDataStorage() \
              .getDataStorageClient(self.mongo_uri, self.mongo_db)
          self.driver = webscrapy.driver

      pass

      # export https://www.bilibili.com/v/douga
      def parseBilibiliAllCategories(self, page):

          bilibiliCategories = list()

          categories = self.scrapy.parseElements([(".sub-nav li a", None)])

          if (categories == None):
              return

          for category in categories:

              item = {}

              item["link"] = category.get_attribute("href")
              item["name"] = category.find_elements_by_css_selector("span").text

              bilibiliCategories.append(item)

          return (categories, "Bilibili_Categories_Collection")


      def parseNextPage(self):

          nextPageButton = self.scrapy.parseElements([("ul.pages li.next button", None)])

          # last page == current page if not click next page to load next video list
          lastPageButtonTxt = self.scrapy.parseElements([("ul.pages li.last button", "text")])
          currentPageButtonTxt = self.scrapy.parseElements([("ul.pages li.active button", "text")])

          if (nextPageButton != None and len(nextPageButton) == 1):
              return nextPageButton[0]
          elif (int(lastPageButtonTxt) == int(currentPageButtonTxt)):
              return None



      # export https://www.bilibili.com/v/douga/tag
      def parseBilibiliSubCategories(self, page):

          tagElements = self.scrapy.parseElements([".tag-list", None])

          # parse tags
          tags = self.parseTags(tagElements)

          hotVideoListElement = self.scrapy.parseElements([(".video-list .tab-list a", None)])
          hotVideoListElement.click()

          # nextPageBtn = self.parseNextPage()

          while ( True ):

             videoList = self.parseHotVideos()

             nextPageBtn = self.parseNextPage()

             if (nextPageBtn != None):
                 nextPageBtn.click()
             else:
                 break


          return videoList

      # parse video information
      def parseVideoInfo(self, v):

          vinfors = v.find_elements_by_css_selector("div.v-info span")

          videoInforItem = {}

          for infor in vinfors:
              videoInforItem["views"] = infor.find_elements_by_css_selector("i.b-icon-v-play span").text()
              videoInforItem["dms"] = infor.find_elements_by_css_selector("i.b-icon-v-dm span").text()
              videoInforItem["favourites"] = infor.find_elements_by_css_selector("i.b-icon-v-fav span").text()

          return videoInforItem

      # parse video uploader information
      def parseUploaderInfo(self, v):

          videoItemUploader = {}

          vuploaderInfor = v.find_elements_by_css_selector("div.up-info")
          videoItemUploader["title"] = vuploaderInfor.find_elements_by_css_selector("a").get_attribute("title")
          videoItemUploader["link"] = vuploaderInfor.find_elements_by_css_selector("a").get_attribute(
              "href")
          videoItemUploader["date"] = vuploaderInfor.find_elements_by_css_selector("span.v-date").text

          return videoItemUploader

      # https://www.bilibili.com/v/douga/mad/#/all/click/0/1/2018-12-28,2019-01-04
      def parseHotVideos(self):

          # https://www.bilibili.com/v/douga/mad/#/all/click/0/1/2018-12-28,2019-01-04
          # parse hot videos
          videoList = list()

          # wait till tag load
          if (self.scrapy.wait_till_visible(".vd-list-cnt .pagination") == True):

              # get all video content
              videoBriefs = self.scrapy.parseElements([(".vd-list li div.r", None)])

              for v in videoBriefs:
                  videoItem = {}

                  videoItem["url"] = v.find_elements_by_css_selector("a").get_attribute("href")
                  videoItem["title"] = v.find_elements_by_css_selector("a").get_attribute("title")
                  videoItem["desc"] = v.find_elements_by_css_selector("div.v-desc").text
                  videoItem["info"] = self.parseVideoInfo(v)
                  videoItem["uploader"] = self.parseUploaderInfo(v)

                  videoList.append(videoItem)


          return videoList


      def parseTags(self, tagListE):

          tags = list()

          tagElements = v.find_elements_by_css_selector("a.tag-a")
          for tagE in tagElements:
              tag = {}
              tag["link"] = tagE.get_attribute("href")
              tag["name"] = tagE.text
              tags.append(tag)

          return tags