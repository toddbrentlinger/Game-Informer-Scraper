import requests
from bs4 import BeautifulSoup
import re
import json
import time

from apiclient.discovery import build
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def isDateTag(tag):
    return tag.name == 'yt-formatted-string' and tag.parent['id'] == 'date'
def isLikesTag(tag):
    return tag.name == 'yt-formatted-string' and tag.has_attr('aria-label') and re.search(' likes', tag['aria-label'])
def isDislikesTag(tag):
    return tag.name == 'yt-formatted-string' and tag.has_attr('aria-label') and re.search(' dislikes', tag['aria-label'])


def getYouTubeData(url):
    # Arguments that need to passed to the build function 
    with open('../../youtube_developer_key.json', 'r') as outfile:
        DEVELOPER_KEY = json.load(outfile)['dev_key']
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
   
    # creating Youtube Resource Object 
    youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
                                            developerKey = DEVELOPER_KEY)

    request = youtube_object.videos().list(
        part="snippet,statistics",
        id=url.split("watch?v=",1)[1]
    )
    response = request.execute()

    youtubeData = {}
    if response['items']:
        # Views
        youtubeData["views"] = int(response["items"][0]["statistics"]["viewCount"])
        # Likes
        youtubeData["likes"] = int(response["items"][0]["statistics"]["likeCount"])
        # Dislikes
        youtubeData["dislikes"] = int(response["items"][0]["statistics"]["dislikeCount"])
        # Thumbnails
        youtubeData["thumbnails"] = response["items"][0]["snippet"]["thumbnails"]
    else:
        print("Could NOT get data from YouTube url: " + url)

    return youtubeData

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