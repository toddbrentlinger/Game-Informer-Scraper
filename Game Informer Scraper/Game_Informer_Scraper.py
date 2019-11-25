
import requests
from bs4 import BeautifulSoup
import re
import json

# TODO

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
        print("*******************************************************")
        print(season.get_text(strip=True))
        print("*******************************************************")

        # Assign int to replaySeason
        replaySeasonString = season.get_text()
        match = re.search(r'\d+', replaySeasonString)
        if match:
            replaySeason = int(match.group(0))
            print("Replay Season " + str(replaySeason))
        else:
            replaySeason = 0
        
        # for each episode of replay
        for replayEpisode in season.parent.find_next_sibling("table").find_all("tr"):
            dataArray = replayEpisode.find_all("td", recursive=False, limit=10)
            if dataArray:
                print("-------------------------------------------------------") # separates each episode

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
                replayEpisodeDict["mainSegmentGames"] = gamesArray

                # system
                systemsArray = []
                for systemString in dataArray[2].stripped_strings:
                    systemsArray.append(systemString.replace('\n',''))
                replayEpisodeDict["system"] = systemsArray
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
                replayEpisodeDict["yearReleased"] = yearReleasedArray

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
                if (arrayLengths[0] != arrayLengths[1] or arrayLengths[1] != arrayLengths[2]):
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

                replayEpisodeArray.append(replayEpisodeDict)
                print(replayEpisodeDict)

        # TEMP 00
        print(allSpecialEpisodesArray)

        # FLAG
        print(flaggedEpisodeArr)

    with open('gameInformerReplayFandomWikiData.json', 'w') as outfile:
        json.dump(replayEpisodeArray, outfile, indent=4)
else:
    print('An error has occurred')

#gameDict = {
#    "title": "",
#    "system": "",
#    "yearReleased": ""
#    }

#EPISODES TO TEST: *1,102, 106, *212, 216, 218, *253, 269, 277
# *307, *320, *322, 324, *331, *344, *347, *349, *355, *361, *362, *366, *379, *392
# *403-408, *412, *414, *422, *443, *444, *449, 452-455, *458, *466, *469, *480, *492
#
#replayEpisodeDict02 = {
#    "episodeNumber": 286,
#    "episodeTitle": "Replay: Prince of Persia: The Sands of Time",
#    "fandomWikiURL": "", # use to get summary of episode and list of host/guests
#    "mainSegmentGames": [
#        {
#            "title": "",
#            "system": "",
#            "yearReleased": ""
#        },
#        {
#            "title": "",
#            "system": "",
#            "yearReleased": ""
#        }
#    ],
#    "airDate": "6/6/15",
#    "videoLength": "1:02:04",
#    "middleSegment": "",
#    "middleSegmentFandomWikiURL": "",
#    "middleSegmentContent": "Nintendo 64 Price Drop and Player's Choice Games Ad",
#    "secondSegment": "RR",
#    "secondSegmentFandomWikiURL": "",
#    "segondSegmentGames": [
#        {
#            "title": "Prince of Persia: The Forgotten Sands",
#            "system": "",
#            "yearReleased": ""
#        },
#        {
#            "title": "",
#            "system": "",
#            "yearReleased": ""
#        }
#    ],
#    "season": 3,
#    "guests": ["host", "guest1", "guest2"],
#    "youTubeURL": "",
#    "youTubeThumbnailURL": "",
#    "youTubeDescription": ""
#}

#                replayEpisodeDict = {
#                    "episodeNumber": 0,
#                    "episodeTitle": dataArray[1].a['title'].replace('\n',''),
#                    "fandomWikiURL": dataArray[1].a['href'],
#                    "mainSegmentGames": [],
#                    "system": [], # dataArray[2].string.replace('\n',''),
#                    "yearReleased": [], # int(dataArray[3].string.replace('\n','')),
#                    "airDate": dataArray[4].get_text(strip=True).replace('\n',''),
#                    "videoLength": dataArray[5].get_text(strip=True).replace('\n',''),
#                    "middleSegment": "", # only in season 3
#                    "middleSegmentContent": "", # only in season 3
#                    "secondSegment": "", # assign Replay Roulette to season 1
#                    "secondSegmentGames": []
#                    }