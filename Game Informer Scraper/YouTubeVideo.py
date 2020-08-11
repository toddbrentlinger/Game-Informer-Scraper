from apiclient.discovery import build
import time
from datetime import date
import pprint
import re
import json

class YouTubeVideo(object):
    # Arguments that need to passed to the build function 
    with open('../../youtube_developer_key.json', 'r') as outfile:
        DEVELOPER_KEY = json.load(outfile)['dev_key']
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    # Access with YouTubeVideo.YOUTUBE_OBJECT
    # OR create in init when first instance is created
    YOUTUBE_OBJECT = build(YOUTUBE_API_SERVICE_NAME, 
                                        YOUTUBE_API_VERSION,
                                        developerKey = DEVELOPER_KEY)

    def __init__(self, videoID):
        # TODO - Check if videoID is valid
        # Check if string
        if not isinstance(videoID, str):
            raise TypeError("Argument 'videoID' is NOT a string.")
        # Check if length is 11 (length of YouTube video ID)
        if len(videoID) > 11:
            # If videoID contains "youtube.com/watch?v=", assume is full URL and get video ID at the end
            if "youtube.com/watch?v=" in videoID:
                videoID = videoID.split("watch?v=",1)[1]
            else:
                raise Exception("Argument 'videoID' is longer than the required 11 characters and NOT a video URL")
        if len(videoID) < 11:
            raise Exception("Argument 'videoID' is less than the required 11 characters.")
        
        self.id = videoID
        self.getYouTubeData()

    def getYouTubeData(self):
        if self.id:
            request = YouTubeVideo.YOUTUBE_OBJECT.videos().list(
                part="snippet,contentDetails,statistics",
                id=self.id
                )
            response = request.execute()
            time.sleep(.5)

            if not response:
                raise Exception("No response from YouTube with video ID:", self.id)

            videoData = response['items'][0]
            # Views
            self.views = int(videoData['statistics']['viewCount'])
            # Likes
            self.likes = int(videoData['statistics']['likeCount'])
            # Dislikes
            self.dislikes = int(videoData['statistics']['dislikeCount'])
            
            # Airdate
            self.airdate = YouTubeVideo.convertYouTubePublishedAtToDateString(
                videoData['snippet']['publishedAt']
            )
            # Title
            self.title = videoData['snippet']['title']
            # Description
            self.description = videoData['snippet']['description']
            # Thumbnails
            self.thumbnails = videoData['snippet']['thumbnails']
            # Tags
            if 'tags' not in videoData['snippet']:
                print(10*"*", f"{self.title} HAS NO TAGS!!!", 10*"*", sep="\n")
            self.tags = videoData['snippet']['tags'] if 'tags' in videoData['snippet'] else []
            # Runtime
            self.runtime = YouTubeVideo.convertYouTubeDuration(
                videoData['contentDetails']['duration']
            )

    def convertToJSON(self):
        return {
            'id': self.id,
            'views': self.views,
            'likes': self.likes,
            'dislikes': self.dislikes,
            'airdate': self.airdate,
            'title': self.title,
            'description': self.description,
            'thumbnails': self.thumbnails,
            'tags': self.tags,
            'runtime': self.runtime
            }

    # ---------- Static Methods ----------

    def getVideoListFromPlaylist(playlistID):
        """Return List of string objects of video ID's using playlistID."""
        if not playlistID:
            raise Exception("No argument provided for parameter: playlistID")
        if not isinstance(playlistID, str):
            raise TypeError("Argument for parameter 'playlistID' is NOT type string")

        request = YouTubeVideo.YOUTUBE_OBJECT.playlistItems().list(
            part="snippet",
            playlistId=playlistID,
            maxResults=50
            )
        response = request.execute()
        time.sleep(.5)

        if not response:
            raise Exception("No response from YouTube with playlist ID:", playlistID)

        videoIdList = []
        for playlistItem in response['items']:
            videoIdList.append(playlistItem['snippet']['resourceId']['videoId'])

        return videoIdList

    def convertYouTubeDuration(youTubeDuration):
        """
        Return string of date in format "DD:HH:MM:SS".

        youTubeDuration - date string in ISO8601 format
        """
        matches = re.match("PT(\d+D)?(\d+H)?(\d+M)?(\d+S)?", youTubeDuration).groups()
        days = YouTubeVideo.convertStringToInt(matches[0]) if matches[0] else 0
        hours = YouTubeVideo.convertStringToInt(matches[1]) if matches[1] else 0
        minutes = YouTubeVideo.convertStringToInt(matches[2]) if matches[2] else 0
        seconds = YouTubeVideo.convertStringToInt(matches[3]) if matches[3] else 0

        durationTuple = (days, hours, minutes, seconds)
        newDurationStr = ""
        for i in range(len(durationTuple)):
            # Skip zeros until get to first nonzero value
            if not durationTuple[i] and not newDurationStr:
                continue
            # If NOT first value added to string and value is less than 10, add zero
            if newDurationStr and durationTuple[i] < 10:
                newDurationStr += "0"
            # Add value to string
            newDurationStr += str(durationTuple[i])
            # Add colon unless last index
            if i < (len(durationTuple) - 1):
                newDurationStr += ":"
        
        # Return string with converted duration in form "DD:HH:MM:SS"
        return newDurationStr

    def convertStringToInt(string):
        """Convert string object to int object"""
        return int("".join([x for x in string if x.isdigit()]))

    def convertYouTubePublishedAtToDateString(publishedAt):
        """
        Convert YouTube publishedAt date to format "Month Day, Year"

        Parameters:
            publishedAt (str): Datetime in ISO 8601 format: "YYYY-MM-DDThh:mm:ss.sZ"
        """
        MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        digits = re.match("(\d+)-(\d+)-(\d+)", publishedAt).groups()
        return f"{MONTHS[int(digits[1]) - 1]} {digits[2]}, {digits[0]}"