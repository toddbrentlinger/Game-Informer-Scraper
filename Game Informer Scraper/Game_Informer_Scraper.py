import requests
from bs4 import BeautifulSoup
import re
import json
import time
import math
from GI_Replay_Fandom_Wiki_Scraper import scrapeGameInformerFandomWiki
from GI_Replay_Episode_Webpage_Scraper import scrapeReplayEpisodeWebpage
from GI_Website_Scraper import scrapeGameInformerArticle
from YouTube_Scraper import scrapeYouTubeURL, getYouTubeData, updateYouTubeData
from YouTube_API import updateYouTubeDataWithAPI
from YouTube_API_Dev_Key import updateYouTubeDataWithAPIDevKey
from Update_Episode_List import updateEpisodeList
from SuperReplayScraper import scrapeSuperReplays
from GI_People_Scraper import scrapePeople

from YouTubeVideo import YouTubeVideo

from Utilities import updateThumbnailImages, updateThumbnailsForSuperReplay

# TODO:
# - Create second array of objects for game data. Reference the game title string in the first array to link
# the data between them.

def changeIndentOfJSON(fileSrc = 'gameInformerReplayFandomWikiData.json', toIndent = True):
    # Open JSON array from local file and save to python list
    with open(fileSrc) as outfile:
        episodeList = json.load(outfile)
    with open(fileSrc, 'w') as outfile:
        if toIndent:
            json.dump(episodeList, outfile, indent=4)
        else:
            json.dump(episodeList, outfile)

def main():
    # Elapsed Time - Start
    startTime = time.time()

    # TODO: Replace 'static' with 'vignette' in image urls
    #updateEpisodeList()
    #scrapeSuperReplays()
    scrapePeople()

    #updateThumbnailImages()
    #updateThumbnailsForSuperReplay()

    #########################################

    #testYTVideo = YouTubeVideo("27GHhA2UFQE")
    #print(testYTVideo.convertToJSON())
    #testYTVideo2 = YouTubeVideo("UrB7Z4vYEd0")
    #print(testYTVideo2.convertToJSON())
    #testYTVideo3 = YouTubeVideo("jNE2xsZWt-Q")
    #print(testYTVideo3.convertToJSON())
    #testYTVideo4 = YouTubeVideo("bzB_ojeWobs")
    #print(testYTVideo4.convertToJSON())

    #updateYouTubeDataWithAPIDevKey()
    #updateEpisodeList()

    #########################################

    #scrapeGameInformerFandomWiki(530, 530)
    #updateYouTubeDataWithAPI(toIndent = False)

    #########################################

    # Scrape webpage with list of replay episodes
    #scrapeGameInformerFandomWiki()
    #time.sleep(1)

    #scrapeGameInformerFandomWiki(528, 528)
    #scrapeGameInformerFandomWiki()

    #updateYouTubeData()
    #updateYouTubeDataWithAPI(toIndent = False)
    #updateYouTubeDataWithAPI('tempGameInformerReplayFandomWikiData.json', False)

    #changeIndentOfJSON(toIndent = True)
    #changeIndentOfJSON('tempGameInformerReplayFandomWikiData.json')

    # Elapsed Time - End
    timeElapsed = time.time() - startTime
    print('\nTime Elapsed: ', math.floor(timeElapsed / 60), 'min:', math.floor(timeElapsed % 60), 'sec')

if __name__ == '__main__':
    main()

def findEpisodesWithNoArticleContent():
    with open('gameInformerReplayFandomWikiData.json', 'r') as outfile:
        episodeList = json.load(outfile)

# TEMP - test array of a few random URLs before running on all episode URLs
#replayEpisodesArray = []
#for episode in tempReplayEpisodeURLArr:
#    replayEpisodesArray.append(scrapeReplayEpisodeWebpage(episode))
#    time.sleep(1) # pause code for a second so not spamming website with requests
# Write JSON to local file
#with open('gameInformerReplayFandomWikiEpisodeData.json', 'w') as outfile:
#    json.dump(replayEpisodesArray, outfile, indent=4)

# Function:
# scrapeReplayEpisode(episodeURL)
def scrapeReplayEpisodeOld(episodeURL):
    baseURL = 'https://replay.fandom.com'
    response = requests.get(baseURL + episodeURL, timeout=5)

    if response:
        content = BeautifulSoup(response.content, "html.parser")

        # Replay episode dictionary to add properties/values
        replayEpisode = {}

        # Content to scrape within tag with id = mw-content-text
        mainContent = content.find(id='mw-content-text')

        # Episode Description
        # TODO: Get all text until next h2 or table tag. Ignore tags(including their children): aside, nav, 
        # TODO: If encounter ul list instead of p, create separate array of list values to append to description array
        # SOLUTION: Recursive function that adds array of list values no matter how deep the hierarchy goes
        episodeDescriptionArr = []
        # Loop through each child tag of the main content
        for child in mainContent.children:
            # Ignore tag aside and tag names that return None
            if child.name is None or child.name == 'aside':
                continue
            # Break loop if enounter h2, table, or nav tags
            if child.name == 'h2' or child.name == 'table' or child.name == 'nav':
                break
            # TODO: Test if the following if-else outputs are equal. If yes, replace with single line
            if child.name == 'ul':
                descriptionText = [text for text in child.stripped_strings]
            else:
                descriptionText = child.get_text().replace('\n', '')
            if descriptionText: # test if empty before appending to array
                episodeDescriptionArr.append(descriptionText)
        # Add array to description property of replayEpisode
        replayEpisode["description"] = episodeDescriptionArr

        # External Links
        # ISSUE: Could have list in description so cannot find first 'ul' tag
        # SOLUTION: use id='External_links'
#        episodeExternalLinksArr = []
#        episodeExternalLinks = mainContent.find('ul')
#        if episodeExternalLinks: # check if there is an unordered list (check is array is empty)
#            for externalLink in episodeExternalLinks.find_all('a'):
#                externalLinkObject = {
#                    "href": externalLink.get('href'),
#                    "title": externalLink.get_text()
#                    }
#                episodeExternalLinksArr.append(externalLinkObject)
#        replayEpisode["externalLinks"] = episodeExternalLinksArr

        # Misc Headers
        # span class='mw-headline' then check for ids and put any unknown header into a separate variable
        episodeExternalLinksArr = []
        episodeNotesArr = []
        episodeQuotesArr = []
        episodeCreditCookiesArr = []
        episodeMiscHeadlinesArr = []
        # NOTE: Might be better to search for all h2 direct children of mainContent
        #for headline in mainContent.find_all('span', 'mw-headline'):
        for headline in mainContent.find_all('h2', recursive=False):
            headlineID = headline.span['id']

            # ----- External Links -----
            if headlineID == 'External_Links' or headlineID == 'External_links':
                # scan each sibling tag until reach table or h2; if anchor tag, copy data
                for sibling in headline.next_siblings:
                    if sibling.name is None:
                        continue
                    if sibling.name == 'table' or sibling.name == 'h2':
                        break
                    for externalLink in sibling.find_all(lambda tag : tag.name == 'a' and tag.find_parent('li')):
                        externalLinkObject = {
                            "href": externalLink.get('href'),
                            "title": externalLink.get_text()
                            }
                        episodeExternalLinksArr.append(externalLinkObject)
                replayEpisode["externalLinks"] = episodeExternalLinksArr

            # ----- Notes -----
            elif headlineID == 'Notes':
                for sibling in headline.next_siblings:
                    if sibling.name is None:
                        continue
                    if sibling.name == 'table' or sibling.name == 'h2':
                        break
                    notesText = sibling.get_text(strip=True)
                    if notesText: # test if empty before appending to array
                        episodeNotesArr.append(notesText)
                replayEpisode["notes"] = episodeNotesArr

            # ----- Quotes -----
            elif headlineID == 'Quotes':
                for sibling in headline.next_siblings:
                    if sibling.name is None:
                        continue
                    if sibling.name == 'table' or sibling.name == 'h2':
                        break
                    quoteText = sibling.get_text(strip=True)
                    if quoteText: # test if empty before appending to array
                        episodeQuotesArr.append(quoteText)
                replayEpisode["quotes"] = episodeQuotesArr

            # ----- Credit Cookie -----
            elif headlineID == 'Credit_Cookie' or headlineID == 'Credit_cookie':
                for sibling in headline.next_siblings:
                    if sibling.name is None:
                        continue
                    if sibling.name == 'table' or sibling.name == 'h2':
                        break
                    creditCookieText = sibling.get_text(strip=True)
                    if creditCookieText: # test if empty before appending to array
                        episodeCreditCookiesArr.append(creditCookieText)
                replayEpisode["creditCookie"] = episodeCreditCookiesArr

            # Misc (add all other headline to single array)
            else:
                miscHeadlineObject = {}
                miscHeadlineTextArr = []
                miscHeadlineObject['id'] = headlineID
                for sibling in headline.next_siblings:
                    if sibling.name is None:
                        continue
                    if sibling.name == 'table' or sibling.name == 'h2':
                        break
                    miscText = sibling.get_text(strip=True)
                    if miscText: # test if empty before appending to array
                        miscHeadlineTextArr.append(miscText)
                miscHeadlineObject['text'] = miscHeadlineTextArr
                episodeMiscHeadlinesArr.append(miscHeadlineObject)

        # After loop finishes, add misc headlines array to replay episode object
        replayEpisode["misc"] = episodeMiscHeadlinesArr

        # Aside
        asideElement = mainContent.find('aside', recursive=False)
        if asideElement: # check if there is an aside element (value is not None)

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
                    imageObject["source"] = imageSrcSet
                else: # else use src attribute
                    imageObject["source"] = [ imageElement.get('src') ]
            replayEpisode["image"] = imageObject

            # System
            # TODO: Make array of strings
            #replayEpisode["system"] = asideElement.find('div', {"data-source": "system"}).get_text()
            systemArr = []
            for systemString in asideElement.find('div', {"data-source": "system"}).div.stripped_strings:
                systemArr.append(systemString.replace('\n', ''))
            replayEpisode["system"] = systemArr

            # Released Date
            # TODO: Make array of strings and ignore sup tags(ex. Ep.1: Twisted Metal 1-4)
            #replayEpisode["gamedate"] = asideElement.find('div', {"data-source": "gamedate"}).get_text()
            gameDateArr = []
            for gameDateString in asideElement.find('div', {"data-source": "gamedate"}).div.stripped_strings:
                gameDateArr.append(gameDateString.replace('\n', ''))
            replayEpisode["gamedate"] = gameDateArr

            # Air Date
            replayEpisode["airdate"] = asideElement.find('div', {"data-source": "airdate"}).div.get_text(strip=True).replace('\n', ' ')

            # Running Time
            replayEpisode["runtime"] = asideElement.find('div', {"data-source": "runtime"}).div.get_text(strip=True).replace('\n', ' ')

            # Host(s)
            hostElement = asideElement.find('div', {"data-source": "host"})
            if hostElement:
                replayEpisode["host"] = [text for text in hostElement.div.stripped_strings]

            # Featuring
            featuringElement = asideElement.find('div', {"data-source": "featuring"})
            if featuringElement:
                replayEpisode["featuring"] = [text for text in featuringElement.div.stripped_strings]

        # Print success message
        print('Replay episode webpage was scrapped!')
        # Return replay episode dictionary
        return replayEpisode
    else:
        print('No response from episode URL: ' + episodeURL)
