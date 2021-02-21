import json

from apiclient.discovery import build
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def updateThumbnailImages():
    # Open JSON array from local file and save to python list
    episodeList = []
    with open('gameInformerReplayFandomWikiData.json', 'r') as outfile:
        episodeList = json.load(outfile)

    # Arguments that need to passed to the build function 
    with open('../../youtube_developer_key.json', 'r') as outfile:
        DEVELOPER_KEY = json.load(outfile)['dev_key']
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
   
    # creating Youtube Resource Object 
    youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
                                            developerKey = DEVELOPER_KEY)

    # For Each replay episode
    for episode in episodeList:
        # Remove original image property
        episode["details"].pop('image', None)

        # Add thumbnails from YouTube Data API
        for link in episode["details"]["external_links"]:
            if ("youtube.com" in link["href"]):
                request = youtube_object.videos().list(
                    part="snippet",
                    id=link["href"].split("watch?v=",1)[1]
                )
                response = request.execute()

                if response['items']:
                    episode["youtube"]["thumbnails"] = response["items"][0]["snippet"]["thumbnails"]
                else:
                    print("Could NOT get data from YouTube video ID: " + link["href"].split("watch?v=",1)[1])

                break # break out of loop of each external links

    # Write updated list to file
    with open('gameInformerReplayFandomWikiData.json', 'w') as outfile:
        json.dump(episodeList, outfile)