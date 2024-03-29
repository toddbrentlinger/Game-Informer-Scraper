import requests
from bs4 import BeautifulSoup
import re
import time

# ISSUE: How to include hyperlinks within paragraphs of text in order to include them when parsing the json in javascript?
# SOLUTION: Save whole paragraph tag as a string and add the element heirarchy exactly as it was Fandom Wiki. Perhaps remove any attributes on the paragraph element.
# TODO: Check for images (ex. Gallery headline)

# - Send first element of mainContent (assuming aside) as argument to get the description content. 
# - Send h2 elements to get other headline data
# - OR send whole main content into function?

def scrapeReplayEpisodeWebpage(episodeURL):
    baseURL = 'https://replay.fandom.com'
    response = requests.get(baseURL + episodeURL, timeout=5)
    time.sleep(.5)

    if response:
        content = BeautifulSoup(response.content, "html.parser")

        # Replay episode dictionary to add properties/values
        replayEpisode = {}

        # ----------------------------------
        # ---------- Main Content ----------
        # ----------------------------------

        # Content to scrape within tag with id = mw-content-text
        mainContent = content.find(id='mw-content-text').find(class_='mw-parser-output')
        
        # Loop through each child tag of the main content
        for child in mainContent.children:
            if child.name is None:
                continue
            # If tag is a headline (tag = 'h2' or 'h3' or has aside as child for description)
            if child.find('aside') or child.name == 'h2' or child.name == 'h3':
                # Get data from each headline
                headlineID, headlineDataArr = get_headline_data(child)
                # Add headline data to episode object
                replayEpisode[headlineID] = headlineDataArr

        # ---------------------------
        # ---------- Aside ----------
        # ---------------------------

        asideElement = mainContent.find('aside')
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
                    imageObject["srcset"] = imageSrcSet
                else: # else use src attribute
                    imageObject["source"] = [ imageElement.get('src') ]
            replayEpisode["image"] = imageObject

            # System
            systemElement = asideElement.find('div', {"data-source": "system"})
            if systemElement:
                replayEpisode["system"] = [text for text in systemElement.div.stripped_strings]

            # Released Date
            # TODO: Make array of strings and ignore sup tags(ex. Ep.1: Twisted Metal 1-4)
            gameDateElement = asideElement.find('div', {"data-source": "gamedate"})
            if gameDateElement:
                replayEpisode["gamedate"] = [text for text in gameDateElement.div.stripped_strings]

            # Air Date
            airdateElement = asideElement.find('div', {"data-source": "airdate"})
            if airdateElement:
                replayEpisode["airdate"] = airdateElement.div.get_text(strip=True).replace('\n', ' ')

            # Running Time
            runningTimeElement = asideElement.find('div', {"data-source": "runtime"})
            if runningTimeElement:
                replayEpisode["runtime"] = runningTimeElement.div.get_text(strip=True).replace('\n', ' ')

            # Host(s)
            hostElement = asideElement.find('div', {"data-source": "host"})
            if hostElement:
                replayEpisode["host"] = [text for text in hostElement.div.stripped_strings]

            # Featuring
            # TODO: Ignore text in between <sup></sup> or add to previous
            # node text in parentheses
            featuringElement = asideElement.find('div', {"data-source": "featuring"})
            if featuringElement:
                replayEpisode["featuring"] = [text for text in featuringElement.div.stripped_strings]

        # Print success message
        print('Replay episode -', content.title.string.split('|')[0], '- webpage was scraped!')

        # Return replay episode dictionary
        return replayEpisode

    else:
        print('No response from episode URL: ' + episodeURL)

def get_headline_data(headline):
    # Raise error if not BeautifulSoup tag
    # if type(headline) != BeatifulSoupTag:
    #   raise TypeError('Headline passed as argument is NOT of type BeatifulSoup tag')
    
    # Assign title of headline
    if headline.find('aside'):
        headlineID = 'description'
    elif headline.span.has_attr('id'):
    # TODO: Check if id matches known id's or convert to lower case before assigning to headlineID
    # (ex. External_links and External_Links with different capitalized 'L')
    # TODO: Get element text for header name instead
        headlineID = headline.span['id'].lower()
    else:
        headlineID = 'unknown'

    # Variable to hold array of headline data
    headlineDataArr = []

    # Scan each sibling tag until reach table, h2, h3
    for sibling in headline.next_siblings:
        # Break if 'video' headline
        if headlineID == 'video': 
            break
        # Break loop if encounter h2, h3, or table tags
        if sibling.name == 'h2' or sibling.name == 'h3' or sibling.name == 'table':
            break
        # Ignore/skip aside, nav, script and tag names that return None
        if sibling.name is None or sibling.name == 'aside' or sibling.name == 'nav' or sibling.name == 'script':
            continue

        # -----------------------
        # External Links/See Also
        # -----------------------
        if headlineID == 'external_links' or headlineID == 'see_also':
            # For each anchor tag that has a li tag parent
            for externalLink in sibling.find_all(lambda tag : tag.name == 'a' and (tag.find_parent('li') or tag.find_parent('p'))):
                        headlineDataArr.append({
                            "href": externalLink.get('href'),
                            "title": externalLink.get_text()
                            })
        # -------
        # Gallery
        # -------
        elif headlineID == 'gallery':
            # For each element with class='wikia-gallery-item'
            for galleryItemElement in sibling.find_all('div', 'wikia-gallery-item'):
                # Find the img and caption element
                imgElement = galleryItemElement.find('img')
                anchorElement = imgElement.find_parent('a')
                headlineDataArr.append({
                    "title": imgElement.get('title'),
                    "src": imgElement.get('src'),
                    "caption": galleryItemElement.find(class_=re.compile("caption")).get_text(strip=True),
                    "link": "https://replay.fandom.com" + anchorElement.get('href'),
                    "height": re.search('(?<=height:)(.*)(?=; width)', anchorElement['style']).group(0),
                    "width": re.search('(?<=width:)(.*)(?=;)', anchorElement['style']).group(0)
                    })

        # ---------------------------------------------------
        # General (Description, Notes, Quotes, Credit Cookie)
        # ---------------------------------------------------
        else:
            # If sibling is list, add array of list values
            if sibling.name == 'ul':
                siblingText = []
                for listItem in sibling.find_all('li'):
                    siblingText.append(listItem.get_text().replace('\n', ''))
                #siblingText = [text for text in sibling.stripped_strings]
            else:
                siblingText = sibling.get_text().replace('\n', '')
            # Test if empty before appending to array
            if siblingText:
                headlineDataArr.append(siblingText)

    # Return tuple of headlineID and headlineDataArr
    return headlineID, headlineDataArr