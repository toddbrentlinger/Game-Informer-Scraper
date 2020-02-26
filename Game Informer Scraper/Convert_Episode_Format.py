import json

def convertEpisodeFormat(fileSrc = 'gameInformerReplayFandomWikiData.json', toIndent = True):
    print('convertEpisodeFormat() started')

    # Open JSON array from local file and save to python list
    with open(fileSrc, 'r') as outfile:
        episodeList = json.load(outfile)

    for episode in episodeList:
        # Episode Number
        pass

    # Write JSON to local file
    with open(fileSrc, 'w') as outfile:
        if toIndent:
            json.dump(episodeList, outfile, indent=4)
        else:
            json.dump(episodeList, outfile)

    print('\n', 'Success. Convert episode format completed!', '\n')