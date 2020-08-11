import requests
import time

from bs4 import BeautifulSoup
from VideoGame import VideoGame
from GI_Replay_Episode_Webpage_Scraper import scrapeReplayEpisodeWebpage
from YouTubeVideo import YouTubeVideo
from GameInformerArticle import GameInformerArticle

class SuperReplayEpisode(object):
    def __init__(self, game, fandomURL = None, youtubeID = None):
        if game and isinstance(game, VideoGame):
            self.game = game

        tempYoutubeURL = ""
        if fandomURL and isinstance(fandomURL, str):
            episodeObj = scrapeReplayEpisodeWebpage(fandomURL)
            
            # Description
            if "description" in episodeObj:
                self.description = SuperReplayEpisode.removeReturnDictValue("description", episodeObj)
            
            # Airdate
            if "airdate" in episodeObj:
                self.airdate = SuperReplayEpisode.removeReturnDictValue("airdate", episodeObj)
            
            # Runtime
            if "runtime" in episodeObj:
                self.runtime = SuperReplayEpisode.removeReturnDictValue("runtime", episodeObj)
            
            # Host
            if "host" in episodeObj:
                self.host = SuperReplayEpisode.removeReturnDictValue("host", episodeObj)
                # Remove any values that include "unofficial"
                self.host = [name for name in self.host if ("unofficial" not in name)]
            
            # Featuring
            if "featuring" in episodeObj:
                self.featuring = SuperReplayEpisode.removeReturnDictValue("featuring", episodeObj)
            
            # External Links
            if "external_links" in episodeObj:
                self.externalLinks = SuperReplayEpisode.removeReturnDictValue("external_links", episodeObj)
                
                # Game Informer Article
                #for link in self.externalLinks:
                #    if "gameinformer.com" in link['href']:
                #        tempGameInformerArticleObj = GameInformerArticle(link['href'].split("gameinformer.com",1)[1])
                #        if tempGameInformerArticleObj:
                #            self.gameInformerArticle = tempGameInformerArticleObj
                #        break

                # YouTube Video
                # Cycle through each link to find youtube url
                for link in self.externalLinks:
                    if "youtube.com/watch?v=" in link['href']:
                        tempYoutubeURL = link['href']

            # Add Fandom URL to top of externalLinks
            #if hasattr(self, 'externalLinks'):
            #    self.externalLinks.insert(0, {
            #        'href': "https://replay.fandom.com" + fandomURL, 
            #        'title': ""
            #    })
            # If YouTube URL NOT in externalLinks, add below first Game Informer article

            # Thumbnail
            # Check if episode thumbnail same as base super replay thumbnail

            # Keys to delete/pop from episodeObj: 'system', 'gamedate', 'image'
            episodeObj.pop('system', None)
            episodeObj.pop('gamedate', None)
            episodeObj.pop('image', None)

            # Add remaining headlines
            self.headlines = episodeObj

        # YouTube Video
        # If youtube video URL was found in external links
        if tempYoutubeURL:
            self.youtubeVideo = YouTubeVideo(tempYoutubeURL)
        # Else If youtube ID is provided as argument
        elif youtubeID:
            self.youtubeVideo = YouTubeVideo(youtubeID)
        else:
            print(
                15*"*",
                f"No YouTube video for {fandomURL}",
                f"given youtubeID: {youtubeID}",
                15*"*",
                sep="\n"
            )

    def scrapeSuperReplayEpisodeFandomPage(fandomURL):
        url = "https://replay.fandom.com" + fandomURL
        response = requests.get(url, timeout=5)
        time.sleep(.5)
        if not response:
            raise Exception("No response from:", url)
        return BeautifulSoup(response.content, "html.parser")

    # ISSUE: If tempValue is reference, will NOT exist when returned after key has been deleted
    def removeReturnDictValue(key, dict):
        # Parameters:
        # key - String of key to remove/return
        # dict - Dictionary to remove/return the key from
        # Return: Value associated with the key in the dictionary
        # Removes key from dictionary and returns the corresponding value
         
        if key in dict:
            tempValue = dict[key]
            del dict[key]
            return tempValue

    def convertToJSON(self):
        tempObj = {}
        if hasattr(self, "description"):
            tempObj["description"] = self.description
        if hasattr(self, "airdate"):
            tempObj["airdate"] = self.airdate
        if hasattr(self, "runtime"):
            tempObj["runtime"] = self.runtime
        if hasattr(self, "host"):
            tempObj["host"] = self.host
        if hasattr(self, "featuring"):
            tempObj["featuring"] = self.featuring
        if hasattr(self, "externalLinks"):
            tempObj["externalLinks"] = self.externalLinks
        if hasattr(self, "headlines"):
            tempObj["headlines"] = self.headlines
        if hasattr(self, "gameInformerArticle") and self.gameInformerArticle:
            tempObj["gameInformerArticle"] = self.gameInformerArticle.convertToJSON()
        if hasattr(self, "youtubeVideo") and self.youtubeVideo:
            tempObj["youtubeVideo"] = self.youtubeVideo.convertToJSON()
        return tempObj