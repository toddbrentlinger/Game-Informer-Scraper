# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import json

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def updateYouTubeDataWithAPI(fileSrc = 'gameInformerReplayFandomWikiData.json', toIndent = True):
    print('updateYouTubeDataWithAPI() started')

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

    # Open JSON array from local file and save to python list
    with open(fileSrc, 'r') as outfile:
        episodeList = json.load(outfile)

    tempEpisodesWithErrorFromScrapeList = []
    for episode in episodeList:
        errorMsg = updateEpisodeYouTubeData(episode, youtube)
        if (errorMsg):
            tempEpisodesWithErrorFromScrapeList.append(errorMsg)

#        # Get youtube URL
#        # If youtube URL was found, scrape url and assign object holding
#        # data to 'youtube' key/property
#        for link in episode["details"]["external_links"]:
#            if ("youtube.com" in link["href"]):
#                request = youtube.videos().list(
#                    part="statistics",
#                    id=link["href"].split("watch?v=",1)[1]
#                )
#                response = request.execute()
#
#                if response:
#                    # If youtube NOT key in episode dict, add as key
#                    if ("youtube" not in episode):
#                        episode["youtube"] = {} 
#                    # Views
#                    episode["youtube"]["views"] = int(response["items"][0]["statistics"]["viewCount"])
#                    # Likes
#                    episode["youtube"]["likes"] = int(response["items"][0]["statistics"]["likeCount"])
#                    # Dislikes
#                    episode["youtube"]["dislikes"] = int(response["items"][0]["statistics"]["dislikeCount"])
#                else:
#                    tempEpisodesWithErrorFromScrapeList.append('Episode: ' + str(episode["episodeNumber"]) + ' could NOT update YouTube data')
#                break

    # Write JSON to local file
    with open(fileSrc, 'w') as outfile:
        if toIndent:
            json.dump(episodeList, outfile, indent=4)
        else:
            json.dump(episodeList, outfile)

    print(tempEpisodesWithErrorFromScrapeList)
    print('\n', 'Success. YouTube API update of episodes completed!', '\n')

def updateEpisodeYouTubeData(episode, youtube):
    # Get youtube URL
    # If youtube URL was found, scrape url and assign object holding
    # data to 'youtube' key/property
    for link in episode["details"]["external_links"]:
        if ("youtube.com" in link["href"]):
            request = youtube.videos().list(
                part="statistics",
                id=link["href"].split("watch?v=",1)[1]
            )
            response = request.execute()

            if response:
                # If youtube NOT key in episode dict, add as key
                if ("youtube" not in episode):
                    episode["youtube"] = {} 
                # Views
                episode["youtube"]["views"] = int(response["items"][0]["statistics"]["viewCount"])
                # Likes
                episode["youtube"]["likes"] = int(response["items"][0]["statistics"]["likeCount"])
                # Dislikes
                episode["youtube"]["dislikes"] = int(response["items"][0]["statistics"]["dislikeCount"])
            else:
                return 'Episode: ' + str(episode["episodeNumber"]) + ' could NOT update YouTube data'
            break