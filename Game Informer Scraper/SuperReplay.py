import requests
import time
import re

from bs4 import NavigableString, BeautifulSoup
from VideoGame import VideoGame
from SuperReplayEpisode import SuperReplayEpisode
from GI_Replay_Episode_Webpage_Scraper import get_headline_data

class SuperReplay(object):
    def __init__(self, superReplayDataList):
        self.number = int(superReplayDataList[0].get_text(strip=True).replace('\n', ''))
        #self.airdate = {
        #    "start": superReplayDataList[4].get_text(strip=True).replace('\n', ''),
        #    "end": superReplayDataList[5].get_text(strip=True).replace('\n', '')
        #    }
        #self.hosts = SuperReplay.getTextListFromAnchorList(superReplayDataList[7])
        
        # List of VideoGame objects
        self.games = []
        tempGamesDict = {}
        tempGamesDict['title'] = SuperReplay.getTextListFromAnchorList(superReplayDataList[1])
        tempGamesDict['system'] = SuperReplay.getTextListFromTextSeparatedByBr(superReplayDataList[2])
        tempGamesDict['yearReleased'] = SuperReplay.getTextListFromTextSeparatedByBr(superReplayDataList[3])
        
        for i in range(len(tempGamesDict['system'])):
            tempTitle = tempGamesDict['title'][i if i < len(tempGamesDict['title']) else 0].replace('\n', '')
            tempSystem = tempGamesDict['system'][i if i < len(tempGamesDict['system']) else 0].replace('\n', '')
            tempYearReleased = tempGamesDict['yearReleased'][i if i < len(tempGamesDict['yearReleased']) else 0].replace('\n', '')
            self.games.append(VideoGame(tempTitle, tempSystem, tempYearReleased))

        # Scrape Super Replay page
        wikiPageURL = "https://replay.fandom.com" + superReplayDataList[1].find('a')['href']
        response = requests.get(wikiPageURL, timeout=5)
        time.sleep(.5)
        if not response:
            raise Exception("No response from:", wikiPageURL)
        content = BeautifulSoup(response.content, "html.parser")

        # Title
        self.title = content.find("h1", "page-header__title").get_text(strip=True).replace('\n', '')

        # ----------------------------------
        # ---------- Main Content ----------
        # ----------------------------------

        self.content = { "description": "" }

        # Content to scrape within tag with id=mw-content-text
        mainContent = content.find(id="mw-content-text")

        # Loop through each child tag of the main content
        for child in mainContent.children:
            # If tag is a headline (tag = 'aside' or 'h2' or 'h3')
            if child.name == 'aside' or child.name == 'h2' or child.name == 'h3':
                # Get data from each headline
                headlineID, headlineDataList = get_headline_data(child)
                # Add headline data to super replay object
                self.content[headlineID] = headlineDataList

        # ---------------------------
        # ---------- Aside ----------
        # ---------------------------

        asideElement = mainContent.find('aside', re.compile("portable-infobox"))

        # Image
        imageObject = {}
        imageElement = asideElement.find('img')
        if imageElement:
            imageObject["width"] = imageElement.get('width')
            imageObject["height"] = imageElement.get('height')
            imageSrcSet = imageElement.get('srcset')
            if imageSrcSet: # check if srcset attribute exists
                imageSrcSet = imageSrcSet.split() # split string at whitespaces
                # remove commas from end of strings (ex. '1x,' in [ 'https://...', '1x,', 'https://...', 2x ])
                imageSrcSet = [ str.strip(',') for str in imageSrcSet ]
                imageObject["srcset"] = imageSrcSet
            else: # else use src attribute
                imageObject["source"] = [ imageElement.get('src') ]
        self.image = imageObject

        # System
        #systemElement = asideElement.find('div', {"data-source": "system"})
        #if systemElement:
        #    replayEpisode["system"] = [text for text in systemElement.div.stripped_strings]

        # Release Date
        releaseDateElement = asideElement.find('div', {"data-source": "gamedate"})
        if releaseDateElement:
            releaseDateList = []
            for child in releaseDateElement.div.children:
                if isinstance(child, NavigableString):
                    releaseDateList.append(child.string.replace('\n', ''))
            # Update games with more accurate release date
            for i in range(len(self.games)):
                self.games[i].releaseDate = releaseDateList[i]

        # Air Date/Episode List
        airdateAndEpisodeElement = asideElement.find('div', {"data-source": "airdate"})
        if airdateAndEpisodeElement:
            self.episodeList = []
            for link in airdateAndEpisodeElement.div.find_all('a'):
                superReplayEpisodeObj = SuperReplayEpisode(self.games[0], link["href"])
                self.episodeList.append(superReplayEpisodeObj)

        # Host(s)
        # Check if matches exisiting hosts property

        # Featuring
        #featuringElement = asideElement.find('div', {"data-source": "featuring"})
        #if featuringElement:
        #    self.featuring = [text for text in featuringElement.div.stripped_strings]

    def __str__(self):
        tempStr = (f"Title: {self.title}\n"
        f"Number: {self.number}\n"
        f"Date: {self.startDate} - {self.endDate}\n"
        f"Hosts: {self.hosts}\n")
        for i in range(len(self.games)):
            tempStr += f"Game {i+1}: {self.games[i]}\n"
        for key in self.content:
            tempStr += f"{key.capitalize()}: {self.content[key]}\n"
        return tempStr

    def getEpisodeCount(self):
        return len(self.episodeList)

    def getTextListFromAnchorList(bs4List):
        # Parameter: List of BeautifulSoup anchor elements
        # Return: List of text of each anchor element as strings
        textList = []
        for anchorElement in bs4List.find_all("a"):
            textList.append(anchorElement.get_text(strip=True).replace('\n', ''))
        return textList

    def getTextListFromTextSeparatedByBr(bs4Obj):
        # Find <br> element(s)
        brElements = bs4Obj.find_all("br")
        # If NO <br> elements, return text from the bs4Obj in a list
        if not brElements:
            return [bs4Obj.get_text(strip=True).replace('\n', '')]

        textList = []
        # First Sibling
        textList.append(str(brElements[0].previous_sibling).replace('\n', ''))
        # Next Sibling(s)
        for brEl in brElements:
            textList.append(str(brEl.next_sibling).replace('\n', ''))

        return textList
    
    def convertToJSON(self):
        tempObj = {}
        if hasattr(self, "title"):
            tempObj["title"] = self.title
        if hasattr(self, "number"):
            tempObj["number"] = self.number
        if hasattr(self, "games"):
            tempObj["games"] = [game.convertToJSON() for game in self.games]
        if hasattr(self, "content"):
            tempObj["content"] = self.content
        if hasattr(self, "image"):
            tempObj["image"] = self.image
        if hasattr(self, "episodeList"):
            tempObj["episodeList"] = [episode.convertToJSON() for episode in self.episodeList]
        return tempObj