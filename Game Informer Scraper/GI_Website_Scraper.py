import requests
from bs4 import BeautifulSoup
import re
import json
import time

def scrapeGameInformerArticle(url):
    baseURL = 'https://www.gameinformer.com'
    response = requests.get(baseURL + url, timeout=5)
    time.sleep(.5)

    if response:
        content = BeautifulSoup(response.content, "html.parser")

        # Game Informer article dictionary to add properties/values
        replayArticle = {}

        # Content to scrape within tag with id = main-content
        mainContent = content.find('main')

        # Title
        titleElement = mainContent.find('h1')
        if titleElement:
            replayArticle["title"] = titleElement.get_text(strip=True)

        # Author
        authorElement = mainContent.find('div', 'author-details')
        if authorElement:
            replayArticle["author"] = authorElement.a.get_text(strip=True)

        # Date
        dateElement = authorElement.a.next_sibling
        if dateElement:
            replayArticle["date"] = dateElement.string.replace('\n', '')
        
        # Content
        replayArticle["content"] = []
        contentElement = content.find(class_=re.compile("text-with-summary"))
        # Cycle direct children paragraph element until reaching paragraph element
        # with video player inside
        for para in contentElement.find_all('p', recursive=False):
            # If para contains video class, break for loop
            if para.find(class_=re.compile("video")) or para.find('img'):
                continue
            # Get all text from paragraph element
            textContent = para.get_text().replace('\n', '')
            # If text is NOT empty, append to article property array
            if textContent:
                replayArticle["content"].append(textContent)

        print("Game Informer article " + replayArticle['title'] + " scraped!")
        return replayArticle