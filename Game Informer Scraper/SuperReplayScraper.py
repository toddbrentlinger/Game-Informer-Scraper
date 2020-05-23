import os.path
import requests
import time
import pprint
import json

from bs4 import BeautifulSoup
from SuperReplay import SuperReplay
from SuperReplayEpisode import SuperReplayEpisode

def scrapeSuperReplays():
    # List to hold SuperReplay objects
    superReplayList = []

    url = 'https://replay.fandom.com/wiki/List_of_Super_Replay_installments'
    response = requests.get(url, timeout=5)
    time.sleep(.5) # Wait after request to limit time between next response
    if not response:
        raise Exception("No response from:", url)
    content = BeautifulSoup(response.content, "html.parser")

    # Official Super Replays
    
    for superReplay in content.find(id="Super_Replays").parent.find_next_sibling("table").find_all("tr"):
        superReplayDataList = superReplay.find_all("td", recursive=False)
        if not superReplayDataList:
            continue

        superReplayObj = SuperReplay(superReplayDataList)
        superReplayList.append(superReplayObj)
        print("\nSuper Replay", superReplayObj.number, "-", superReplayObj.title, "has been scraped!\n")

    # TEMP - Testing
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(superReplayList[0].convertToJSON())
    #return

    with open('gameInformerSuperReplayFandomWikiData.json', 'w') as outfile:
        superReplayListJSON = []
        for superReplay in superReplayList:
            superReplayListJSON.append(superReplay.convertToJSON())
        json.dump(superReplayListJSON, outfile, indent=4)