import requests
import time
import re

from bs4 import BeautifulSoup

class GameInformerArticle(object):
    def __init__(self, url):
        if not isinstance(url, str):
            raise Exception("Argument 'url' is NOT a string")

        self.url = url

        self.scrapeGameInformerArticle(url)

    def scrapeGameInformerArticle(self, url):
        # Parameter: 
        # url - end of url to be appended to https://www.gameinformer.com
        # Scrapes Game Informer article and assigns properties to instance
        
        completeURL = "https://www.gameinformer.com" + url
        response = requests.get(completeURL, timeout=5)
        time.sleep(.5)
        
        if not response:
            self.title = ""
            self.author = ""
            self.date = ""
            self.content = []
            print("NO response from:", completeURL)
        else:
            content = BeautifulSoup(response.content, "html.parser")

            # Content to scrape within tag with id = main-content
            mainContent = content.find('main')

            # Title
            titleElement = mainContent.find('h1')
            if titleElement:
                self.title = titleElement.get_text(strip=True)

            # Author
            authorElement = mainContent.find('div', 'author-details')
            if authorElement:
                self.author = authorElement.a.get_text(strip=True)

            # Date
            dateElement = authorElement.a.next_sibling
            if dateElement:
                self.date = dateElement.string.replace('\n', '')
        
            # Content
            self.content = []
            contentElement = content.find(class_=re.compile("text-with-summary"))
            # Cycle direct children paragraph element until reaching paragraph element
            # with video player inside
            for para in contentElement.find_all('p', recursive=False):
                # If para contains video class, break for loop
                if para.find(class_=re.compile("video")):
                    break
                # Get all text from paragraph element
                textContent = para.get_text().replace('\n', '')
                # If text is NOT empty, append to article property array
                if textContent:
                    self.content.append(textContent)

            print("Game Informer article:", self.title, "was scraped!")

    def convertToJSON(self):
        return {
            "url": self.url,
            "title": self.title,
            "author": self.author,
            "date": self.date,
            "content": self.content
            }
