from bs4 import BeautifulSoup

# ISSUE: How to include hyperlinks within paragraphs of text in order to include them when parsing the json in javascript?
# SOLUTION: Save whole paragraph tag as a string and add the element heirarchy exactly as it was Fandom Wiki. Perhaps remove any attributes on the paragraph element.
# TODO: Check for images (ex. Gallery headline)

# - Send first element of mainContent (assuming aside) as argument to get the description content. 
# - Send h2 elements to get other headline data
# - OR send whole main content into function?

def get_headline_data(headline):
    # Raise error if not BeautifulSoup tag
#    if type(headline) != BeatifulSoupTag:
#        raise TypeError('Headline passed as argument is NOT of type BeatifulSoup tag')

    # Assign title of headline
    if headline.name == 'aside':
        headlineID = 'description'
    elif headline.span.has_attr('id'):
    # TODO: Check if id matches known id's or convert to lower case before assigning to headlineID
    # (ex. External_links and External_Links with different capitalized 'L')
        headlineID = headline.span['id'].lower()
    else:
        headlineID = 'unknown'

    # Variable to hold array of headline data
    headlineDataArr = []

    # Scan each sibling tag until reach table or h2
    for sibling in headline.next_siblings:
        # Break loop if encounter h2, table, or nav tags
        if sibling.name == 'h2' or sibling.name == 'table' or sibling.name == 'nav':
            break
        # Ignore/skip aside tag and tag names that return None
        if sibling.name is None or sibling.name == 'aside'or sibling.name == 'script':
            continue

        # --------------
        # External Links
        # --------------
        if headlineID == 'external_links':
            # For each anchor tag that has a li tag parent
            for externalLink in sibling.find_all(lambda tag : tag.name == 'a' and tag.find_parent('li')):
                        headlineDataArr.append({
                            "href": externalLink.get('href'),
                            "title": externalLink.get_text()
                            })

        # -------
        # Gallery
        # -------
        elif headlineID == 'gallery':
            pass

        # --------------------------------------------
        # General (Description, Notes, Quotes, Credit Cookie)
        # --------------------------------------------
        else:
            # If sibling is list, add array of list values
            if sibling.name == 'ul':
                siblingText = [text for text in sibling.stripped_strings]
            else:
                siblingText = sibling.get_text(strip=True).replace('\n', '')
            # Test if empty before appending to array
            if siblingText:
                headlineDataArr.append(siblingText)

    # Return tuple of headlineID and headlineDataArr
    return headlineID, headlineDataArr