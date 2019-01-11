# -*- coding: utf-8 -*-
import datetime
import pprint

from selenium.common.exceptions import NoSuchElementException

from WebScraper import BaseClassWithWeakReferenceCount, WebScrapyMongoDataStorage, WebScrapy


class BilibiliDotComCrawler(BaseClassWithWeakReferenceCount):

      mongo_uri = 'mongodb://localhost:27017',
      mongo_db = 'bilibili_video_db'

      def __init__(self, webscrapy):

          super(BaseClassWithWeakReferenceCount, self).__init__()

          self.start_url = "https://www.bilibili.com/"

          self.today = datetime.date.today().strftime('%Y-%m-%d')
          self.mongo_db = 'bilibili_video_db_' + self.today

          self.dataStorage = WebScrapyMongoDataStorage() \
              .getDataStorageClient(self.mongo_uri, self.mongo_db)

          self.driver = webscrapy.driver
          self.scrapy = webscrapy

      # export https://www.bilibili.com/v/douga
      def parseBilibiliAllCategories(self, page):

          pprint.pprint("start parsing:" + page)

          self.scrapy.load_page(page)

          appE = self.scrapy.parseElements([("#app", "element")])[0]

          bilibiliCategories = list()

          categories = self.scrapy.parseElements([("#primary_menu li a", "element")])

          for category in categories:

              item = {}

              print(category.get_attribute("href"))
              print(category.get_attribute("innerHTML"))

              item["link"] = category.get_attribute("href")

              try:

                 spanEl = category.find_element_by_xpath("./span")
                 item["name"] = spanEl.get_attribute("innerHTML")
                 bilibiliCategories.append(item)

              except NoSuchElementException:
                  continue


          print(bilibiliCategories)

          if (len(bilibiliCategories) > 0) :
              self.dataStorage.saveAllToStorage(bilibiliCategories, "Bilibili_Category_Collection")

          return bilibiliCategories


      def parseNextPage(self):

          nextPageButton = self.scrapy.parseElements([("ul.pages li.next button", "element")])

            # last page == current page if not click next page to load next video list
          if (nextPageButton != None and len(nextPageButton) == 1):
              return nextPageButton[0]
          else:
              return None


      # export https://www.bilibili.com/v/douga
      def parseBilibiliSubCategories(self, page, isMostPopular):

          print("start parsing:" + page)

          self.scrapy.load_page(page)

          tagElements = self.scrapy.parseElements([(".tag-list", "element")])

          # parse tags
          tags = self.parseTags(tagElements)

          pprint.pprint(tags)
          if (len(tags) > 0):
              self.dataStorage.saveAllToStorage(tags, "Bilibili_Category_Tag_Collection")

          subnav = self.scrapy.parseElements([("#subnav .on a", "element")])

          if (len(subnav) > 0):
              currentSubNav = subnav[0]

              currentElement = {}

              currentElement["Link"] = currentSubNav.get_attribute("href")
              currentElement["Name"] = currentSubNav.get_attribute("innerHTML")
              currentElement["hotTags"] = tags

              print(currentElement)

              if (isMostPopular == True) :
                  return self.getFirst20PagesOfLatestVideos(currentElement)
              else:
                  return self.getFirst20PagesOfMostPopularVideos(currentElement)

      def getFirst20PagesOfLatestVideos(self, currentElement):

          videoListTag = self.scrapy.parseElements([(".video-list .left .tab-list a:first-child", "element")])

          if (len(videoListTag) > 0):

            latestVideoListLink = videoListTag[0]

            print(latestVideoListLink.get_attribute("href"))

            return self.getVideosOfPages(latestVideoListLink.get_attribute("href"), currentElement)

          return dict()

      def getFirst20PagesOfMostPopularVideos(self, currentElement):

          videoListTag = self.scrapy.parseElements([(".video-list .left .tab-list a:last-child", "element")])

          if (len(videoListTag) > 0):

              hotVideoListLink = videoListTag[0]

              print(hotVideoListLink.get_attribute("href"))

              return self.getVideosOfPages(hotVideoListLink.get_attribute("href"), currentElement)

          return dict()


      def getVideosOfPages(self, page, currentElement):

          self.scrapy.load_page(page)

          videoListTag = self.scrapy.parseElements([(".video-list .right .tab-list .mod-1", "element")])

          if (len(videoListTag) > 0):

              listViewElement = videoListTag[0]
              listViewElement.click()

              # totalVideoList = list()
              totalVideoMap = dict()

              for i in range(2):

                  self.parseHotVideos(totalVideoMap, currentElement["Link"])

                  nextPageBtn = self.parseNextPage()

                  if (nextPageBtn != None):
                      nextPageBtn.click()
                  else:
                      break

                  print(i)


              if (len(totalVideoMap) > 0):
                 self.dataStorage.saveAllToStorage(totalVideoMap.values(), "Bilibili_Categories_videos_Collection")

              return totalVideoMap

          return list()


      # parse video information
      def parseVideoInfo(self, v):

          vinfors = v.find_elements_by_css_selector("div.v-info")

          videoInforItem = {}

          for infor in vinfors:

              if (self.scrapy.wait_till_visible(".b-icon-v-play + span", 10) == True):
                  videoInforItem["views"] = infor.find_element_by_css_selector(".b-icon-v-play + span")\
                      .get_attribute("innerHTML")
                  print("views:" + videoInforItem["views"])

              if (self.scrapy.wait_till_visible(".b-icon-v-fav + span", 10) == True):
                  videoInforItem["favourites"] = infor.find_element_by_css_selector(".b-icon-v-fav + span") \
                      .get_attribute("innerHTML")
                  print("favourites:" + videoInforItem["favourites"])

              if (self.scrapy.wait_till_visible(".b-icon-v-dm + span", 10) == True):
                  videoInforItem["dms"] = infor.find_element_by_css_selector(".b-icon-v-dm + span")\
                     .get_attribute("innerHTML")
                  print("dms:" + videoInforItem["dms"])



          pprint.pprint(videoInforItem)

          return videoInforItem

      def parseTagToElementWrapper(self, cssSelectors):
          elements = self.scrapy.parseElements(cssSelectors)
          if ( len(elements) > 0 ):
              return elements[0]
          else:
              return None





      #bilibiliLinkTemplate = "https://www.bilibili.com/video/av{0}"
      def parseVideoDetails(self, videoDetails, videoBrief):

          self.scrapy.load_page(videoBrief["url"])


          bilibiliVideoItem = {}

          bilibiliVideoItem["videoId"] = videoBrief["url"]

          if (len(self.scrapy.parseElements([(".error-text", "element")])) > 0):
              return

          propertyMap = {"coinCount": [(".coin-box", "title"), (".ops .coin", "title")],
                         "likeCount": [(".ops .like", "title")],
                         "favouriteCount": [(".fav-box", "title"), (".ops .collect", "title")],
                         "shareCount": [(".playpage_share div", "title"), (".share-box .s-text", "title"), (".ops .share-box", "title")],
                         "viewCount": [(".bili-wrapper .video-info-m .play", "title"), (".video-data .view", "title")],
                         "subtitleCount": [(".bilibili-player-danmaku-number", "title"), (".video-data .dm", "title")],
                         "uploadedAt" : [(".bili-wrapper .tm-info time", "text"), (".video-data time", "text")],
                         "userProfileLink": [("#v_upinfo .u-face a", "href"), (".u-info .name a", "href")],
                         "userName": [(".user .name", "text"), (".u-info .name .username", "text")],
                         "isVip": [(".user .is-vip", None), (".u-info .name .is-vip", "boolean")],
                         "userSignature": [(".info .sign span", "text"), (".u-info .desc", "text")],
                         "videoDetails": [("#v_desc", "text")],
                         "subscription": [(".info .number span:last-child", "title"), (".followwe span.gz", "text")],
                         "commentsSize": [(".common .b-head span:first-child", "text")],
                         "videoDuration": [("span.bilibili-player-video-time-total", "text")],
                         "videoTitle": [(".bili-wrapper .video-info-m h1", "title"), (".video-title", "title")]}

          for propertyMapEntry in propertyMap:
              prop = propertyMapEntry[0]
              cssSelectors = propertyMapEntry[1]
              bilibiliVideoItem[prop] = self.parseTagToElementWrapper(cssSelectors)

          pprint.pprint(bilibiliVideoItem)

          if (bilibiliVideoItem["videoTitle"] != None):
              videoDetails.append(bilibiliVideoItem)


      # parse video uploader information
      def parseUploaderInfo(self, v):

          videoItemUploader = {}

          vuploaderInfor = v.find_element_by_css_selector("div.up-info")
          videoItemUploader["title"] = vuploaderInfor.find_element_by_css_selector("a")\
              .get_attribute("title")
          videoItemUploader["link"] = vuploaderInfor.find_element_by_css_selector("a")\
              .get_attribute("href")
          videoItemUploader["date"] = vuploaderInfor.find_element_by_css_selector("span.v-date")\
              .get_attribute("innerHTML")

          pprint.pprint(videoItemUploader)

          return videoItemUploader

      # https://www.bilibili.com/v/douga/mad/#/all/click/0/1/2018-12-28,2019-01-04
      def parseHotVideos(self, totalVideoMap, subcategoryLink):

          # https://www.bilibili.com/v/douga/mad/#/all/click/0/1/2018-12-28,2019-01-04
          # parse hot videos
          # videoList = list()

          # wait till tag load
          if (self.scrapy.wait_till_visible(".vd-list-cnt .pagination",10) == True):

              # get all video content
              videoBriefs = self.scrapy.parseElements([(".vd-list li div.r", "element")])

              for v in videoBriefs:
                  videoItem = {}

                  videoItem["subcategoryLink"] = subcategoryLink
                  videoItem["url"] = v.find_element_by_css_selector("a").get_attribute("href")
                  videoItem["title"] = v.find_element_by_css_selector("a").get_attribute("title")

                  print(videoItem["title"])

                  videoItem["desc"] = v.find_element_by_css_selector("div.v-desc").text
                  videoItem["info"] = self.parseVideoInfo(v)
                  videoItem["uploader"] = self.parseUploaderInfo(v)

                  print(videoItem)

                  # totalVideoList.append(videoItem)
                  totalVideoMap[videoItem["url"]] = videoItem

          pprint.pprint(totalVideoMap.values())

          # return videoList


      def parseTags(self, vlist):

          tags = list()

          if (len(vlist) > 0 ):

              tagElements = vlist[0].find_elements_by_css_selector("a.tag-a")
              for tagE in tagElements:
                  tag = {}
                  tag["link"] = tagE.get_attribute("href")
                  tag["name"] = tagE.text
                  tags.append(tag)

          pprint.pprint(tags)

          return tags

def mergeKeySet(dict1, dict2):

    keySet = videoDictMostPopular.keys()

    for key in keySet:
        dict1.add(dict2.get(key))



if __name__ == '__main__':

   webscrape = WebScrapy("Chrome")

   bilibiliDotComCrawler =  BilibiliDotComCrawler(webscrape)

   bilibiliCategories = bilibiliDotComCrawler.parseBilibiliAllCategories(bilibiliDotComCrawler.start_url)


   for categoryItem in bilibiliCategories:

       keySet = set()
       resultDict = dict()

       print(categoryItem["link"])

       videoDictMostPopular = bilibiliDotComCrawler.parseBilibiliSubCategories(categoryItem["link"], True)
       mergeKeySet(resultDict, videoDictMostPopular)

       videoDictLastest = bilibiliDotComCrawler.parseBilibiliSubCategories(categoryItem["link"], False)
       mergeKeySet(resultDict, videoDictLastest)

       items = resultDict.values()

       bilibiliDotComCrawler.dataStorage.saveAllToStorage(items, "Bilibili_videos_detail_Collection")














