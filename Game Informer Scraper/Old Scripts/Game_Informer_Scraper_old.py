import requests
from bs4 import BeautifulSoup
import re
import json
import time
from GI_Replay_Episode_Webpage_Scraper import get_headline_data

# TODO:
# - Create second array of objects for game data. Reference the game title string in the first array to link
# the data between them.

tempReplayEpisodeURLArr = [
    '/wiki/Replay:_The_Jaguar_Disaster',
    '/wiki/Replay:_Xena:_Warrior_Princess',
    '/wiki/Replay:_Gex:_Enter_the_Gecko',
    '/wiki/Replay:_Twisted_Metal_1–4',
    '/wiki/Replay:_Halloween_Stuptacular!',
    '/wiki/Replay:_The_Sniper_2',
    '/wiki/Replay:_Sonic_Adventure',
    '/wiki/Replay:_Quest_64',
    '/wiki/Replay:_Bushido_Blade',
    '/Replay:_Silent_Hill:_Downpour',
    '/wiki/Replay:_Crystal%27s_Pony_Tale',
    '/wiki/Replay:_Dragon_Ball_Z:_Chou_Saiya_Densetsu'
    ]

# Functions for Beautiful Soup find_all()
#def anchor_child_of_li(tag):
#    return tag.name == 'a' and tag.find_parent('li')

# TEMP Function:
def scrapeReplayEpisode(episodeURL):
    baseURL = 'https://replay.fandom.com'
    response = requests.get(baseURL + episodeURL, timeout=5)

    if response:
        content = BeautifulSoup(response.content, "html.parser")

        # Replay episode dictionary to add properties/values
        replayEpisode = {}

        # Content to scrape within tag with id = mw-content-text
        mainContent = content.find(id='mw-content-text')

        # Loop through each child tag of the main content
        for child in mainContent.children:
            if child.name == 'aside' or child.name == 'h2':
                headlineID, headlineDataArr = get_headline_data(child)
                replayEpisode[headlineID] = headlineDataArr
        
        # Print success message
        print('Replay episode webpage was scrapped!')

        # Return replay episode dictionary
        return replayEpisode

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

# TEMP - test array of a few random URLs before running on all episode URLs
#replayEpisodesArray = []
#for episode in tempReplayEpisodeURLArr:
#    replayEpisodesArray.append(scrapeReplayEpisode(episode))
#    time.sleep(1) # pause code for a second so not spamming website with requests
# Write JSON to local file
#with open('gameInformerReplayFandomWikiEpisodeData.json', 'w') as outfile:
#    json.dump(replayEpisodesArray, outfile, indent=4)

# Function: scrapeGameInformerFandomWiki()
# scrapeGameInformerFandomWiki(startEpisode = 1, endEpisode = 0, scrapeEachEpisodeSite = false)
# startEpisode - earliest episode to include
# endEpisode - default value of 0 corresponds to most recent episode listed on site (could also use most recent episode number)
# scrapeEachEpisodeSite - boolean to scrape additional data of each episode using each indiviual episode webpage
def scrapeGameInformerFandomWiki(startEpisode = 1, endEpisode = 0, scrapeEachEpisodeSite = True):
    url = 'https://replay.fandom.com/wiki/List_of_Replay_episodes'
    response = requests.get(url, timeout=5)

    if response:
        content = BeautifulSoup(response.content, "html.parser")

        replaySeason = 0
        replayEpisodeArray = []
        flaggedEpisodeArr = []

        # TEMP 00
        allSpecialEpisodesArray = []

        # for each season
        for season in content.find_all("span", text=re.compile("Season")):

            # Print season number
            print("\n*******************************************************\n",
                  season.get_text(strip=True),
                  "\n*******************************************************\n",
                  )
            # print(season.get_text(strip=True))
            # print("*******************************************************")

            # Assign int to replaySeason
            replaySeasonString = season.get_text()
            match = re.search(r'\d+', replaySeasonString)
            if match:
                replaySeason = int(match.group(0))
                #print("Replay Season " + str(replaySeason))
            else:
                replaySeason = 0
        
            # for each episode of replay
            for replayEpisode in season.parent.find_next_sibling("table").find_all("tr"):
                dataArray = replayEpisode.find_all("td", recursive=False, limit=10)
                if dataArray:
                    # empty dict to assign keys and values for current episode
                    replayEpisodeDict = {}

                    # episodeNumber
                    replayEpisodeDict["episodeNumber"] = int(dataArray[0].get_text(strip=True).replace('\n',''))

                    # episodeTitle
                    replayEpisodeDict["episodeTitle"] = dataArray[1].a['title'].replace('\n','')

                    # fandom wiki URL
                    replayEpisodeDict["fandomWikiURL"] = dataArray[1].a['href']

                    # mainSegmentGames
                    gamesArray = []
                    for gameString in dataArray[1].stripped_strings:
                        if not gameString.endswith(":"): # exclude titles of special episodes
                            if gameString.endswith(","): # remove comma at end of title if part of list
                                gameString = gameString[:-1]
                            gamesArray.append(gameString)
                    #replayEpisodeDict["mainSegmentGames"] = gamesArray

                    # system
                    systemsArray = []
                    for systemString in dataArray[2].stripped_strings:
                        systemsArray.append(systemString.replace('\n',''))
                    #replayEpisodeDict["system"] = systemsArray
                    # FLAG if system needs manual edit
                    if len(systemsArray) != 1 and len(systemsArray) != len(gamesArray):
                        flaggedEpisodeArr.append({"episode": replayEpisodeDict["episodeNumber"], "system": systemsArray})

                    # yearReleased
                    yearReleasedArray = []
                    for yearString in dataArray[3].stripped_strings:
                        yearReleasedArray.append(yearString.replace('\n',''))
                        # FLAG if year released is a range
                        if yearString.find("-") != -1:
                            flaggedEpisodeArr.append({"episode": replayEpisodeDict["episodeNumber"],
                                                      "yearReleased": yearString})
                    #replayEpisodeDict["yearReleased"] = yearReleasedArray

                    # create array of game objects, each with title, system, and releaseDate
                    # ISSUE: Some episodes are special and include the title as the first game (ex. 320 Turbographx Special)
                    # which assigns wrong system and year to actual games
                    # SOLUTION: Use length of yearReleasedArray to control length of array of gameObjects
                    # and ignore first game title if gamesArray length is one more than yearReleasedArray
                    mainSegmentGamesArrayAdv = []
                    arrayLengths = [ len(gamesArray), len(systemsArray), len(yearReleasedArray) ]
                    arrLength = max(arrayLengths)
                    for i in range(arrLength):
                        gameObject = {}
                        # add title
                        gameObject["title"] = gamesArray[i if i < arrayLengths[0] else arrayLengths[0] - 1]
                        # add system
                        gameObject["system"] = systemsArray[i if i < arrayLengths[1] else arrayLengths[1] - 1]
                        # add yearReleased
                        gameObject["yearReleased"] = yearReleasedArray[i if i < arrayLengths[2] else arrayLengths[2] - 1]
                        # append gameObject to array of games
                        mainSegmentGamesArrayAdv.append(gameObject)
                    # add array of games to episode dictionary
                    replayEpisodeDict["mainSegmentGamesAdv"] = mainSegmentGamesArrayAdv

                    # TEMP 00
                    if (arrayLengths[1] != 1 and arrayLengths[0] != arrayLengths[1]) or (arrayLengths[2] != 1 and arrayLengths[1] != arrayLengths[2]):
                        allSpecialEpisodesArray.append([replayEpisodeDict["episodeNumber"], arrayLengths[0], arrayLengths[1], arrayLengths[2]])
                    
                    # airDate
                    replayEpisodeDict["airDate"] = dataArray[4].get_text(strip=True).replace('\n','')

                    # videoLength
                    replayEpisodeDict["videoLength"] = dataArray[5].get_text(strip=True).replace('\n','')

                    # middleSegment / middleSegmentContent (only for season 3)
                    # TODO: Only add key/value for episodes in Season 3. Don't include in other seasons
                    if replaySeason == 3:
                        replayEpisodeDict["middleSegment"] = dataArray[6].get_text(strip=True).replace('\n','')
                        replayEpisodeDict["middleSegmentContent"] = dataArray[7].get_text(strip=True).replace('\n','')

                    # secondSegment (assign RR to first season)
                    if replaySeason == 1:
                        index = 5
                        replayEpisodeDict["secondSegment"] = "RR"
                    else:
                        index = 8 if replaySeason==3 else 6
                        replayEpisodeDict["secondSegment"] = dataArray[index].get_text(strip=True).replace('\n','')

                    # secondSegmentGames
                    secondSegmentGamesArray = []
                    # SPECIAL CASE: check if there is a missing tag element (see episode 379)
                    # OR use last element of dataArray assuming it will always be secondSegmentGames
                    if len(dataArray) == index+2:
                        for gameString in dataArray[index+1].stripped_strings:
                            secondSegmentGamesArray.append(gameString)
                    replayEpisodeDict["secondSegmentGames"] = secondSegmentGamesArray

                    # season
                    replayEpisodeDict["season"] = replaySeason

                    # Append replay episode dict to array to episodes
                    replayEpisodeArray.append(replayEpisodeDict)

                    print(replayEpisodeDict, end='\n-------------------------------------------------------\n')

        # TEMP 00
        print()
        for specialEpisode in allSpecialEpisodesArray:
            print(specialEpisode)

        # FLAG: Print array of flagged episodes
        print()
        for flaggedEpisode in flaggedEpisodeArr:
            print(flaggedEpisode)

        # Write JSON to local file
        with open('gameInformerReplayFandomWikiData.json', 'w') as outfile:
            json.dump(replayEpisodeArray, outfile, indent=4)

        print('\n', 'Success. Web scrape completed!', '\n')
    else:
        print('An error has occurred')
