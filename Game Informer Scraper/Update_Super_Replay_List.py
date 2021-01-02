import requests
from bs4 import BeautifulSoup
import time
import json
from SuperReplay import SuperReplay
from YouTube_API_Dev_Key import updateEpisodeYouTubeDataWithDevKey

def updateSuperReplayList():
    # Get Super Replay (SR) list
    # Get SR number from first SR on list (base SR number)
    # Scrape each SR if SR number is greater than base SR number
    # Break loop and do NOT scrape any more SR is SR number is equal to or less than base SR number
    # Add new SR to top of SR list
    # Update YouTube data for all SR episodes

    # Open JSON array from local file and save to python list
    superReplayList = []
    with open('gameInformerSuperReplayFandomWikiData.json', 'r') as outfile:
        superReplayList = json.load(outfile)

    # Get base SR number from first SR on JSON list
    baseSRNumber = 0
    if (superReplayList[0]['number']):
        baseSRNumber = int(superReplayList[0]['number'])

    # Scrape each SR if SR number is greater than base SR number
    # Scrape all SR is base SR number is zero
    url = "https://replay.fandom.com/wiki/List_of_Super_Replay_installments"
    response = requests.get(url, timeout=5)
    time.sleep(.5)
    if not response:
        raise Exception("No response from: ", url)

    content = BeautifulSoup(response.content, 'html.parser')
    superReplaysScraped = 0
    newSuperReplayList = []

    for superReplay in content.find(id='Super_Replays').parent.find_next_sibling('table').find_all('tr'):
        superReplayDataList = superReplay.find_all('td', recursive=False)
        if not superReplayDataList:
            continue

        superReplayNum = int(superReplayDataList[0].get_text(strip=True).replace("\n", ""))

        # Break loop if superReplayNum is less than or equal to baseSRNumber
        if superReplayNum <= baseSRNumber:
            break

        # Create SR object
        superReplayObj = superReplay(superReplayDataList)

        # Append to newSuperReplayList
        newSuperReplayList.append(superReplayObj)

        superReplaysScraped += 1

    # Add new SR to top of superReplayList
    if (len(newSuperReplayList) > 0):
        superReplayList = newSuperReplayList + superReplayList

    print("\n", "Success. Web scrape completed with", superReplaysScraped, "Super Replays!", "\n")

    # Update YouTube data for all SR episodes

if __name__ == "__main__":
    updateSuperReplayList()