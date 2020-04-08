import requests
import time

from bs4 import BeautifulSoup
from VideoGame import VideoGame
from GI_Replay_Episode_Webpage_Scraper import scrapeReplayEpisodeWebpage

class SuperReplayEpisode(object):
    def __init__(self, game = VideoGame(), fandomURL = ""):
        self.game = game
        if fandomURL:
            self.youtube = {
                "id": "",
                "views": 0,
                "likes": 0
                }

        if fandomURL:
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
            # Featuring
            if "featuring" in episodeObj:
                self.featuring = SuperReplayEpisode.removeReturnDictValue("featuring", episodeObj)
            # External Links
            if "external_links" in episodeObj:
                self.externalLinks = SuperReplayEpisode.removeReturnDictValue("external_links", episodeObj)
            # Image
            # Check if episode image same as base super replay image

            # Add remaining headlines
            self.headlines = episodeObj

    def scrapeSuperReplayEpisodeFandomPage(fandomURL):
        url = "https://replay.fandom.com" + fandomURL
        response = requests.get(url, timeout=5)
        time.sleep(.5)
        if not response:
            raise Exception("No response from:", url)
        content = BeautifulSoup(rresponse.content, "html.parser")

    def removeReturnDictValue(key, dict):
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
        if hasattr(self, "headlines"):
            tempObj["headlines"] = self.headlines
        return tempObj