import requests
from bs4 import BeautifulSoup
import re
import json
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
    time.sleep(.5)
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
            youTubeDict["views"] = int(re.search('\d.*\d', viewsNode.text.strip()).group(0).replace(',', ''))

        # Date
        #dateNode = content.find(isDateTag)
        #if dateNode:
        #    youTubeDict["date"] = dateNode.get_text(strip=True).replace('Premiered ', '')

        # Likes
        likesNode = content.find('button', title='I like this')
        if likesNode:
            #youTubeDict["likes"] = likesNode.get_text(strip=True)
            youTubeDict["likes"] = int(likesNode.text.strip().replace(',', ''))

        # Dislikes
        dislikesNode = content.find('button', title='I dislike this')
        if dislikesNode:
            #youTubeDict["dislikes"] = dislikesNode.get_text(strip=True)
            youTubeDict["dislikes"] = int(dislikesNode.text.strip().replace(',', ''))

        print("YouTube video scraped!")

        return youTubeDict

# TODO: Check if views/likes are empty before assigning to each episode
def updateYouTubeData():
    print('updateYouTubeData() started')

    # Open JSON array from local file and save to python list
    with open('gameInformerReplayFandomWikiData.json', 'r') as outfile:
        episodeList = json.load(outfile)

    tempEpisodesWithErrorFromScrapeList = []
    for episode in episodeList:
        # Get youtube URL
        # If youtube URL was found, scrape url and assign object holding
        # data to 'youtube' key/property
        for link in episode["details"]["external_links"]:
            if ("youtube.com" in link["href"]):
                # Assign object returned from scrape to temp variable
                tempScrapedObj = scrapeYouTubeURL(link["href"])
                # If youtube NOT key in episode dict, add as key
                if ("youtube" not in episode):
                    episode["youtube"] = {}
                # Compare each key/value pair before assigning to episode
                for key, value in tempScrapedObj.items():
                    if (value or value == 0):
                        episode["youtube"][key] = value
                    else:
                        tempEpisodesWithErrorFromScrapeList.append('Episode: ' + str(episode["episodeNumber"]) + ' - ' + str(key) + ' is empty')
                #episode["youtube"] = scrapeYouTubeURL(link["href"])
                print('Episode ' + str(episode["episodeNumber"]) + ' was scraped!')
                break

    # Write JSON to local file
    with open('gameInformerReplayFandomWikiData.json', 'w') as outfile:
        json.dump(episodeList, outfile, indent=4)

    print(tempEpisodesWithErrorFromScrapeList)
    print('\n', 'Success. YouTube scrape of episode completed!', '\n')