import requests
from bs4 import BeautifulSoup
import re
import time

def isDateTag(tag):
    return tag.name == 'yt-formatted-string' and tag.parent['id'] == 'date'
def isLikesTag(tag):
    return tag.name == 'yt-formatted-string' and tag.has_attr('aria-label') and re.search(' likes', tag['aria-label'])
def isDislikesTag(tag):
    return tag.name == 'yt-formatted-string' and tag.has_attr('aria-label') and re.search(' dislikes', tag['aria-label'])


# Function: scrapeYouTubeURL(url)
def scrapeYouTubeURL(url):
    response = requests.get(url, timeout=5)
    time.sleep(.7)
    if response:
        content = BeautifulSoup(response.content, "html.parser")

        # YouTube dictionary to add properties/values
        youTubeDict = {}

        # Content to scrape within tag with id="info"
        #infoNode = content.find(id='info')
        #print(infoNode)

        # Views
        viewsNode = content.find(class_='watch-view-count')
        if viewsNode:
            #youTubeDict["views"] = re.search('\d.*\d' , viewsNode.get_text()).replace(',','')
            youTubeDict["views"] = re.search('\d.*\d', viewsNode.text.strip()).group(0).replace(',', '')

        # Date
        #dateNode = content.find(isDateTag)
        #if dateNode:
        #    youTubeDict["date"] = dateNode.get_text(strip=True).replace('Premiered ', '')

        # Likes
        likesNode = content.find('button', title='I like this')
        if likesNode:
            #youTubeDict["likes"] = likesNode.get_text(strip=True)
            youTubeDict["likes"] = likesNode.text.strip()

        # Dislikes
        dislikesNode = content.find('button', title='I dislike this')
        if dislikesNode:
            #youTubeDict["dislikes"] = dislikesNode.get_text(strip=True)
            youTubeDict["dislikes"] = dislikesNode.text.strip()

        print("YouTube video scraped!")

        return youTubeDict