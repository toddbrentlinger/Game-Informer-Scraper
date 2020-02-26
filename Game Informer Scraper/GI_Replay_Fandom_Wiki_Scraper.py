import requests
from bs4 import BeautifulSoup
import re
import json
import time
from GI_Replay_Episode_Webpage_Scraper import scrapeReplayEpisodeWebpage
from GI_Website_Scraper import scrapeGameInformerArticle
from YouTube_Scraper import scrapeYouTubeURL

# Function: scrapeGameInformerFandomWiki()
# scrapeGameInformerFandomWiki(startEpisode = 1, endEpisode = 0, scrapeEachEpisodeSite = false)
# startEpisode - earliest episode to include
# endEpisode - default value of 0 corresponds to most recent episode listed on site (could also use most recent episode number)
# scrapeEachEpisodeSite - boolean to scrape additional data of each episode using each indiviual episode webpage
# OR
# startEpisode/endEpisode should both default to zero
# If both are zero, scrape all episodes
# Else If both nonzero, scrape numbers in range startEpisode:endEpisode
# Else If startEpisode nonzero (end must be zero), scrape from startEpisode to most recent episode
# Else endEpisode nonzero (start must be zero), scrape from earliest episode to endEpisode

def scrapeGameInformerFandomWiki(startEpisode = 0, endEpisode = 0, scrapeEachEpisodeSite = True, scrapeEachGIArticle = True, scrapeYouTubeVideo = True):
    url = 'https://replay.fandom.com/wiki/List_of_Replay_episodes'
    response = requests.get(url, timeout=5)
    time.sleep(.5)

    if response:
        content = BeautifulSoup(response.content, "html.parser")

        replaySeason = 0
        replayEpisodeArray = []
        flaggedEpisodeArr = []

        # TEMP 00
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
                    # If endEpisode is zero, assign to most recent episodeNumber
                    if not endEpisode:
                        endEpisode = episodeNumber
                    # Since list is displayed in descending order from most recent to earliest,
                    # If episodeNumber is more than argument endEpisode, continue
                    if episodeNumber > endEpisode:
                        continue;
                    # Else If episodeNumber is less than argument startEpisode, break
                    elif episodeNumber < startEpisode:
                        break;

                    ########

                    # empty dict to assign keys and values for current episode
                    replayEpisodeDict = {}

                    # episodeNumber
                    replayEpisodeDict["episodeNumber"] = episodeNumber

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

                    # Season
                    replayEpisodeDict["season"] = replaySeason

                    # Scrape separate webpage about specific replay episode
                    if scrapeEachEpisodeSite:
                        replayEpisodeDict["details"] = scrapeReplayEpisodeWebpage(replayEpisodeDict["fandomWikiURL"])

                        # Scrape Game Informer article if link is provided from separate page scrape
                        # Scrape YouTube url if link is provided
                        if scrapeEachGIArticle or scrapeYouTubeVideo:
                            for link in replayEpisodeDict["details"]["external_links"]:
                                if ( ("gameinformer.com" in link["href"]) and ("article" not in replayEpisodeDict.keys()) ):
                                    replayEpisodeDict["article"] = scrapeGameInformerArticle(link["href"].split("gameinformer.com", 1)[1])
                                    break # break out of loop in case other links from gameinformer.com
                                elif (("youtube.com" in link["href"]) and ("youtube" not in replayEpisodeDict.keys()) ):
                                    replayEpisodeDict["youtube"] = scrapeYouTubeURL(link["href"])

                    # Append replay episode dict to array of episodes
                    replayEpisodeArray.append(replayEpisodeDict)

                    print("Episode " + str(episodeNumber) + " has been scraped!")

                    ####################

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

def scrapeReplayEpisode(dataArray, replaySeason):
    # empty dict to assign keys and values for current episode
    replayEpisodeDict = {}

    # episodeNumber
    replayEpisodeDict["episodeNumber"] = episodeNumber

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

    # Season
    replayEpisodeDict["season"] = replaySeason

    # Scrape separate webpage about specific replay episode
    if scrapeEachEpisodeSite:
        replayEpisodeDict["details"] = scrapeReplayEpisodeWebpage(replayEpisodeDict["fandomWikiURL"])

        # Scrape Game Informer article if link is provided from separate page scrape
        # Scrape YouTube url if link is provided
        if scrapeEachGIArticle or scrapeYouTubeVideo:
            for link in replayEpisodeDict["details"]["external_links"]:
                if ( ("gameinformer.com" in link["href"]) and ("article" not in replayEpisodeDict.keys()) ):
                    replayEpisodeDict["article"] = scrapeGameInformerArticle(link["href"].split("gameinformer.com", 1)[1])
                    break # break out of loop in case other links from gameinformer.com
                elif (("youtube.com" in link["href"]) and ("youtube" not in replayEpisodeDict.keys()) ):
                    replayEpisodeDict["youtube"] = scrapeYouTubeURL(link["href"])

    # Return replay episode dict to append to array of episodes
    print("Episode " + str(episodeNumber) + " has been scraped!")
    return replayEpisodeDict