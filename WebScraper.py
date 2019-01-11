import time

import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
import selenium.webdriver.support.expected_conditions as EC
from weakref import WeakValueDictionary

class BaseClassWithWeakReferenceCount(object):

    _instances = WeakValueDictionary()

    def __init__(self):
        self._instances[id(self)] = self

class WebScrapyMongoDataStorage(BaseClassWithWeakReferenceCount):

     db = None
     client = None

     def __init__(self):
         super(BaseClassWithWeakReferenceCount, self).__init__()

     def getDataStorageClient(self, databaseURI, dbname):
         client = pymongo.MongoClient(databaseURI)
         self.db = client[dbname]
         return self

     def saveOneToStorage(self, obj, collectionName):
         self.db[collectionName].insert_one(dict(obj))

     def saveAllToStorage(self, collection, collectionName):
         print(collectionName)
         self.db[collectionName].insert_many(collection)

     def __del__(self):

         if (self.db == None):
             return

         self.db.client.close()


class WebScrapy(BaseClassWithWeakReferenceCount):

    driver = None


    def getChromeDriver(self):
        chrome_driver_path = "/Users/shannon/serenium_drivers/chromedriver"
        return webdriver.Chrome(chrome_driver_path)

    def getFireFoxDriver(self):
        firefox_driver_path = "/Users/shannon/serenium_drivers/gechodriver"
        return webdriver.Firefox(firefox_driver_path)

    def __init__(self, driveType):

        # super(self)

        super(WebScrapy, self).__init__()

        if (driveType == "FireFox"):
            self.driver = self.getFireFoxDriver()

        elif (driveType == "Chrome"):
            self.driver = self.getChromeDriver()

    def load_page(self, pageUri):
         self.driver.get(pageUri)

    # return True if element is visible within 2 seconds, otherwise False
    def wait_till_visible(self, locator, timeout=2):
        try:
            ui.WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, locator)))
            return True
        except TimeoutException:
            return False

    def wait_till_element_located(self, locator, timeout=2):
        try:
            ui.WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, locator)))
            return True
        finally:
            return False

    # return True if element is not visible within 2 seconds, otherwise False
    def is_not_visible(self, locator, timeout=2):
        try:
            ui.WebDriverWait(self.driver, timeout).until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, locator)))
            return True
        except TimeoutException:
            return False

    def parseElements(self, cssSelecors):

          retSet = list()

          for cssSelector in cssSelecors:

              print(cssSelector)

              if (self.wait_till_visible(cssSelector[0], 10) == True):

                  print(cssSelector[0])

                  elements = self.driver.find_elements_by_css_selector(cssSelector[0])

                  attribute = cssSelector[1]

                  eSize = len(elements)

                  if (eSize > 0):
                     # return elements

                      for element in elements:

                          print(element.get_attribute("innerHTML"))
                          print(attribute)

                          if (attribute == "text"):
                              retSet.append(element.text)

                          elif (attribute == "element"):
                              retSet.append(element)

                          elif (attribute == "boolean"):
                              retSet.append(True)

                          else:
                              retSet.append(element.get_attribute(attribute))


          return retSet

    def implicitWaitScrollToEnd(self):

        SCROLL_PAUSE_TIME = 0.5

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def __del__(self):

        if (self.driver == None):
            return

        self.driver.close()
        self.driver.quit()