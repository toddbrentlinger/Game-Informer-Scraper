from apiclient.discovery import build
import json

def updateYouTubeDataWithAPIDevKey():
    print('updateYouTubeDataWithAPIKey() started')

    # Arguments that need to passed to the build function 
    DEVELOPER_KEY = "AIzaSyDullnHxGG5X_MZXBHAXJFmKEdn7gohUR4" 
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
   
    # creating Youtube Resource Object 
    youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
                                            developerKey = DEVELOPER_KEY)

    # Open JSON array from local file and save to python list
    with open('gameInformerReplayFandomWikiData.json', 'r') as outfile:
        episodeList = json.load(outfile)

    tempEpisodesWithErrorFromScrapeList = []
    for episode in episodeList:
        errorMsg = updateEpisodeYouTubeDataWithDevKey(episode, youtube_object)
        if (errorMsg):
            tempEpisodesWithErrorFromScrapeList.append(errorMsg)

    # Write JSON to local file
    with open('gameInformerReplayFandomWikiData.json', 'w') as outfile:
        json.dump(episodeList, outfile)

    print(tempEpisodesWithErrorFromScrapeList)
    print('\n', 'Success. YouTube API update of episodes using API dev key completed!', '\n')

def updateEpisodeYouTubeDataWithDevKey(episode, youtube_object):
    # Get youtube URL
    # If youtube URL was found, scrape url and assign object holding
    # data to 'youtube' key/property
    for link in episode["details"]["external_links"]:
        if ("youtube.com" in link["href"]):
            request = youtube_object.videos().list(
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

class YouTubeAPIDevKey(object):
    # Arguments that need to passed to the build function 
    DEVELOPER_KEY = "AIzaSyDullnHxGG5X_MZXBHAXJFmKEdn7gohUR4" 
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    # Access with YouTubeAPIDevKey.YOUTUBE_OBJECT
    # OR create in init when first instance is created
    YOUTUBE_OBJECT = build(YOUTUBE_API_SERVICE_NAME, 
                                        YOUTUBE_API_VERSION,
                                        developerKey = DEVELOPER_KEY)

    def __init__(self):
       # Create Youtube Resource Object 
       if not self.youtube_object:
            self.youtube_object = build(YOUTUBE_API_SERVICE_NAME, 
                                        YOUTUBE_API_VERSION,
                                        developerKey = DEVELOPER_KEY)

    def updateEpisode(episode):
        # Get youtube URL
        # If youtube URL was found, scrape url and assign object holding
        # data to 'youtube' key/property
        for link in episode["details"]["external_links"]:
            if ("youtube.com" in link["href"]):
                request = self.youtube_object.videos().list(
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

    def updateEpisodeList():
        # Open JSON array from local file and save to python list
        with open('gameInformerReplayFandomWikiData.json', 'r') as outfile:
            episodeList = json.load(outfile)

        tempEpisodesWithErrorFromScrapeList = []
        for episode in episodeList:
            errorMsg = self.updateEpisode(episode)
            if (errorMsg):
                tempEpisodesWithErrorFromScrapeList.append(errorMsg)

        # Write JSON to local file
        with open('gameInformerReplayFandomWikiData.json', 'w') as outfile:
            json.dump(episodeList, outfile)

        print(tempEpisodesWithErrorFromScrapeList)
        print('\n', 'Success. YouTube API update of episodes using API dev key completed!', '\n')