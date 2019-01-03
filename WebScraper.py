import time

import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
import selenium.webdriver.support.expected_conditions as EC
from weakref import WeakValueDictionary

class BaseClassWithWeakReferenceCount():

    _instances = WeakValueDictionary()

    def __init__(self):
        self._instances[id(self)] = self

class WebScrapyMongoDataStorage(BaseClassWithWeakReferenceCount):

     def __init__(self):
         super(self)

     def getDataStorageClient(self, databaseURI, dbname):
         client = pymongo.MongoClient(databaseURI)
         self.db = client[dbname]
         return self.db

     def saveOneToStorage(self, (obj, collectionName)):
         self.db[collectionName].insert_one(dict(obj))

     def saveAllToStorage(self, (objs, collectionName)):
         self.db[collectionName].insert_all(objs)

     def __del__(self):
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

        super(self)

        if (driveType == "FireFox"):
            self.driver = self.getFireFoxDriver()

        elif (driveType == "Chrome"):
            self.driver = self.getChromeDriver()

    # return True if element is visible within 2 seconds, otherwise False
    def is_visible(self, locator, timeout=2):
        try:
            ui.WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, locator)))
            return True
        except TimeoutException:
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

              elements = self.driver.find_elements_by_css_selector(cssSelector[0])
              attribute = self.driver.find_elements_by_css_selector(cssSelector[1])

              eSize = len(elements)

              print(eSize)

              if (eSize > 0):
                  return elements

              for element in elements:
                  if (attribute == "text" and element.text != None):
                      retSet.append(element.text)

                  elif (attribute == "text" and element.text == None):
                      retSet.append(element)

                  elif (attribute == "text" and element.text == "Html"):
                      retSet.append(element.get_arrtibute("innerHtml"))

                  elif (attribute == "Boolean"):
                      retSet.append(True)
                  else:
                      retSet.append(element.get_arrtibute(attribute))


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