
import requests
from bs4 import BeautifulSoup
import re
import datetime

# return true if tag is h2 and text includes 'season'
def game(tag):
    return (tag.name == "h2") and tag.find("span", text=re.compile("Season"))

url = 'https://replay.fandom.com/wiki/List_of_Replay_episodes'
response = requests.get(url, timeout=5)

if response:
    content = BeautifulSoup(response.content, "html.parser")

#    for replayEpisode in content.find_all("h2", text=re.compile("Season")): #href=re.compile("/wiki/Replay") #string=re.compile("Season")
#        print(replayEpisode.text.encode('utf-8'))

    replaySeason = 0
    replayEpisodeArray = []
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

        for replayEpisode in season.parent.find_next_sibling("table").find_all("tr"):
            dataArray = replayEpisode.find_all("td", recursive=False, limit=10)
            if dataArray:
                print("-------------------------------------------------------") # separates each episode
                replayEpisodeDict = {
                    "episodeNumber": 0,
                    "episodeTitle": dataArray[1].a['title'].replace('\n',''),
                    "fandomWikiURL": dataArray[1].a['href'],
                    "mainSegmentGames": [],
                    "system": [], # dataArray[2].string.replace('\n',''),
                    "yearReleased": [], # int(dataArray[3].string.replace('\n','')),
                    "airDate": dataArray[4].get_text(strip=True).replace('\n',''),
                    "videoLength": dataArray[5].get_text(strip=True).replace('\n',''),
                    "middleSegment": "", # only in season 3
                    "middleSegmentContent": "", # only in season 3
                    "secondSegment": "", # assign Replay Roulette to season 1
                    "secondSegmentGames": []
                    }
                # episodeNumber
                replayEpisodeDict["episodeNumber"] = int(dataArray[0].get_text(strip=True).replace('\n',''))

                # mainSegmentGames
                gamesArray = []
                for gameString in dataArray[1].stripped_strings:
                    gamesArray.append(gameString)
                replayEpisodeDict["mainSegmentGames"] = gamesArray

                # system
                systemsArray = []
                for systemString in dataArray[2].stripped_strings:
                    systemsArray.append(systemString.replace('\n',''))
                replayEpisodeDict["system"] = systemsArray

                # yearReleased
                yearReleasedArray = []
                for yearString in dataArray[3].stripped_strings:
                    yearReleasedArray.append(yearString.replace('\n',''))
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

                # middleSegment / middleSegmentContent (only for season 3)
                # TODO: Only add key/value for episodes in Season 3. Don't include in other seasons
                if replaySeason==3:
                    replayEpisodeDict["middleSegment"] = dataArray[6].get_text(strip=True).replace('\n','')
                    replayEpisodeDict["middleSegmentContent"] = dataArray[7].get_text(strip=True).replace('\n','')

                # secondSegment
                if replaySeason == 1:
                    index = 5
                    replayEpisodeDict["secondSegment"] = "RR"
                else:
                    index = 8 if replaySeason==3 else 6
                    replayEpisodeDict["secondSegment"] = dataArray[index].get_text(strip=True).replace('\n','')

                # secondSegmentGames
                secondSegmentGamesArray = []
                # SPECIAL CASE: check if there is a missing tag element (see episode 379)
                if len(dataArray) == index+2:
                    for gameString in dataArray[index+1].stripped_strings:
                        secondSegmentGamesArray.append(gameString)
                replayEpisodeDict["secondSegmentGames"] = secondSegmentGamesArray

                #replayEpisodeArray.append(replayEpisodeObject)
                print(replayEpisodeDict)
            #for data in dataArray:
            #    print(data.string) # data.text.encode('utf-8')
        # set season value to apply to each replay episode

#        EPISODES TO TEST: 102, 106, 212, 216, 218, 269, 320, 379, 492
#        replayEpisodeObject = {
#            "episodeNumber": 286,
#            "episodeTitle": "Prince of Persia: The Sands of Time",
#            "fandomWikiURL": "", # use to get summary of episode and list of host/guests
#            "mainSegmentGames": [Prince of Persia: The Sands of Time],
#            "system": "[PS3]",
#            "yearReleased": [2010],
#            "airdate": "6/6/15",
#            "videoLength": "1:02:04",
#            "middleSegment": "",
#            "middleSegmentFandomWikiURL": "",
#            "middleSegmentContent": "Nintendo 64 Price Drop and Player's Choice Games Ad",
#            "secondSegment": "Replay Roulette",
#            "secondSegmentFandomWikiURL": "",
#            "secondSegmentGames": ["Prince of Persia: The Forgotten Sands"],
#
#            "mainSegmentGames": [
#                {
#                    "title": "",
#                    "system": "",
#                    "yearReleased": ""
#                },
#                {
#                    "title": "",
#                    "system": "",
#                    "yearReleased": ""
#                 }
#              ],
#
#            "season": 3,
#            "guests": [host, guest01, guest02, ...],
#
#            "youtubeURL": "",
#            "youtubeImageURL": "",
#            "youtubeDescription": ""
#            }

else:
    print('An error has occurred')

gameDict = {
    "title": "",
    "system": "",
    "yearReleased": ""
    }