import requests
from bs4 import BeautifulSoup
import re
import time
import json
from GI_Replay_Fandom_Wiki_Scraper import scrapeReplayEpisode
from YouTube_API import updateEpisodeYouTubeData

from apiclient.discovery import build
from YouTube_API_Dev_Key import updateEpisodeYouTubeDataWithDevKey

import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def updateEpisodeList():
    # Get episode list
    # Get episode number from first episode on list (base episode number)
    # Scrape each episode if episode number is greater than base episode number
    # Break loop and do NOT scrape any more episodes if episode number is equal to or less than base episode number
    # Add new episodes to top of episode list
    # Update YouTube data for all episodes

    # Open JSON array from local file and save to python list
    episodeList = []
    with open('gameInformerReplayFandomWikiData.json', 'r') as outfile:
        episodeList = json.load(outfile)

    # Get episode number from first episode on list (base episode number)
    baseEpisodeNumber = 0
#    if type(episodeList[0]['episodeNumber']) == type(baseEpisodeNumber):
#        baseEpisodeNumber = episodeList[0]['episodeNumber']
    if (episodeList[0]['episodeNumber']):
        baseEpisodeNumber = int(episodeList[0]['episodeNumber'])

    # Scrape each episode if episode number is greater than base episode number
    # Scrape all episodes if episode number is 0
    url = 'https://replay.fandom.com/wiki/List_of_Replay_episodes'
    response = requests.get(url, timeout=5)
    time.sleep(.5)

    if response:
        content = BeautifulSoup(response.content, "html.parser")

        replaySeason = 0
        episodesScraped = 0
        replayEpisodeArray = []
        flaggedEpisodeArr = []
        allSpecialEpisodesArray = []

        # for each season
        for season in content.find_all("span", text=re.compile("Season")):

            # Assign int to replaySeason
            match = re.search(r'\d+', season.get_text())
            replaySeason = int(match.group(0)) if match else 0
        
            # For each episode of replay
            for replayEpisode in season.parent.find_next_sibling("table").find_all("tr"):
                dataArray = replayEpisode.find_all("td", recursive=False, limit=10)
                if dataArray:
                    # Check arguments if episode number should be included
                    episodeNumber = int(dataArray[0].get_text(strip=True).replace('\n',''))
                    
                    # If episodeNumber is less than or equal to baseEpisodeNumber, break
                    if episodeNumber <= baseEpisodeNumber:
                        break

                    # Append replay episode dict to array of episodes
                    replayEpisodeTuple = scrapeReplayEpisode(dataArray, episodeNumber, replaySeason)
                    replayEpisodeArray.append(replayEpisodeTuple[0])

                    # Increment episodes scraped counter
                    episodesScraped += 1

                    # Add flagged episode
                    if (len(replayEpisodeTuple[1]) > 0):
                        flaggedEpisodeArr.append(replayEpisodeTuple[1])
                    if (len(replayEpisodeTuple[2]) > 0):
                        allSpecialEpisodesArray.append(replayEpisodeTuple[2])

        # TEMP 00
        print()
        for specialEpisode in allSpecialEpisodesArray:
            print(specialEpisode)
        # FLAG: Print array of flagged episodes
        print()
        for flaggedEpisode in flaggedEpisodeArr:
            print(flaggedEpisode)

        # Add new episodes to top of episode list
        if (len(replayEpisodeArray) > 0):
            episodeList = replayEpisodeArray + episodeList

        print('\n', 'Success. Web scrape completed with',  episodesScraped, 'episodes!', '\n')
    else:
        print('No response from url: ', url)

    # Update YouTube data for all episodes

    # Arguments that need to passed to the build function 
    DEVELOPER_KEY = "AIzaSyDullnHxGG5X_MZXBHAXJFmKEdn7gohUR4" 
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
   
    # creating Youtube Resource Object 
    youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
                                            developerKey = DEVELOPER_KEY)

    tempEpisodesWithErrorFromScrapeList = []
    for episode in episodeList:
        errorMsg = updateEpisodeYouTubeDataWithDevKey(episode, youtube_object)
        if (errorMsg):
            tempEpisodesWithErrorFromScrapeList.append(errorMsg)

    with open('gameInformerReplayFandomWikiData.json', 'w') as outfile:
        json.dump(episodeList, outfile)

    print(tempEpisodesWithErrorFromScrapeList)
    print('\n', 'Success. Update episode list completed!', '\n')

def oldYouTubeUpdate():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "../../client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    tempEpisodesWithErrorFromScrapeList = []
    for episode in episodeList:
        errorMsg = updateEpisodeYouTubeData(episode, youtube)
        if (errorMsg):
            tempEpisodesWithErrorFromScrapeList.append(errorMsg)

    with open('gameInformerReplayFandomWikiData.json', 'w') as outfile:
        json.dump(episodeList, outfile)

    print(tempEpisodesWithErrorFromScrapeList)
    print('\n', 'Success. Update episode list completed!', '\n')