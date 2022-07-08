import pprint

from bs4 import NavigableString

class Person(object):
    """
    Class representing a Person

    Attributes:
        personData: (<BeautifulSoupTag Object>): BeautifulSoup Tag object from web scrape
    """
    def __init__(self, person_data):
        """
        Constructor for Person class.

        Parameters:
            personData: (<BeautifulSoupTag Object>): BeautifulSoup Tag object from web scrape
        """
        # Full Name
        self.name = person_data.find(class_='page-header__title').get_text(strip=True)

        # Main
        main_content = person_data.find(class_='mw-parser-output')

        # Main - Info Box
        info_box = main_content.find(class_='portable-infobox')

        # Main - Info Box - Image
        imageObject = {}
        image_element = info_box.find(class_='pi-image-thumbnail')
        if image_element:
            imageObject["width"] = int(image_element.get('width'))
            imageObject["height"] = int(image_element.get('height'))
            imageSrcSet = image_element.get('srcset')
            if imageSrcSet: # check if srcset attribute exists
                imageSrcSet = imageSrcSet.split() # split string at whitespaces
                # remove commas from end of strings (ex. '1x,' in [ 'https://...', '1x,', 'https://...', 2x ])
                imageSrcSet = [ str.strip(',') for str in imageSrcSet ]
                imageObject["srcset"] = imageSrcSet
            else: # else use src attribute
                imageObject["source"] = [ image_element.get('src') ]
        self.image = imageObject

        # Main - Info Box - Details
        self.info_box_details = {}
        for detail_element in info_box.find_all('div', class_='pi-item'):
            label = detail_element.find(class_='pi-data-label').get_text(strip=True).lower()
            
            value_element = detail_element.find(class_='pi-data-value')
            value_list = []

            # Check if value element has list of values (<br> separating them) or single value
            if value_element.br:
                for child in value_element.children:
                    if child.name == 'br': continue
                    print(child)
                    value_list.append(self.get_info_detail_values(child))
            else:
                value_list.append(self.get_info_detail_values(value_element))

            #value_anchor_link = value_element.find('a')
            #if value_anchor_link is not None:
            #    value = {
            #        'href': value_anchor_link.get('href'),
            #        'text': value_anchor_link.get_text(strip=True)
            #    }
            #else:
            #    value = value_element.get_text(strip=True)

            self.info_box_details[label] = value_list

        # First child is 'p' element that holds info box info.
        # Start with second child
        child = list(main_content.children)[1]

        # Description
        # Get all 'p' elements until reaching stop (ex. h2, h3) or end (table)
        self.description = []
        while child and child.name not in ('h2', 'h3', 'table'):
            if child.name is not None and child.name == 'p':
                child_text = child.get_text().replace('\n', '')
                if child_text:
                    self.description.append(str(child_text))
            child = child.next_sibling

        self.headings = {}
        # Other headers after description
        while child and child.name is not 'table':
            if child.name in ('h2', 'h3'):
                heading_title_id = child.find(class_='mw-headline').get('id').lower()
                # Skip Replay Appearance AND Super Replay Appearances
                if heading_title_id not in ('replay_appearances', 'super_replay_appearances'):
                    # Variable to hold array of headline data
                    headlineDataArr = []

                    # Scan each sibling tag until reach table, h2, h3
                    for sibling in child.next_siblings:
                        # Break loop if encounter h2, h3, or table tags
                        if sibling.name in ('h2', 'h3', 'table'):
                            break
                        # Ignore/skip aside, nav, script and tag names that return None
                        if sibling.name is None or sibling.name == 'aside' or sibling.name == 'nav' or sibling.name == 'script':
                            continue

                        # -----------------------
                        # External Links/See Also
                        # -----------------------
                        if heading_title_id == 'external_links' or heading_title_id == 'see_also':
                            # For each anchor tag that has a li tag parent
                            for externalLink in sibling.find_all(lambda tag : tag.name == 'a' and (tag.find_parent('li') or tag.find_parent('p'))):
                                        headlineDataArr.append({
                                            "href": externalLink.get('href'),
                                            "title": externalLink.get_text()
                                            })
                        # -------
                        # Gallery
                        # -------
                        elif heading_title_id == 'gallery':
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
                                    "height": int(re.search('(?<=height:)(.*)(?=; width)', anchorElement['style']).group(0)),
                                    "width": int(re.search('(?<=width:)(.*)(?=;)', anchorElement['style']).group(0))
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
                            elif sibling.name == 'figure':
                                siblingText = self.get_figure_data(sibling)
                            else:
                                siblingText = sibling.get_text().replace('\n', '')
                            # Test if empty before appending to array
                            if siblingText:
                                headlineDataArr.append(siblingText)
                    self.headings[heading_title_id] = headlineDataArr
            child = child.next_sibling

    def get_info_detail_values(self, value_element):
        if isinstance(value_element, NavigableString):
            return str(value_element)

        value_anchor_link = value_element.find('a')
        if value_anchor_link is not None:
            return {
                'href': value_anchor_link.get('href'),
                'text': value_anchor_link.get_text(strip=True)
            }
        else:
            return value_element.get_text(strip=True)

    def get_figure_data(self, figure_element):
        output = {}

        # Image
        img_element = figure_element.find('img')
        output['image'] = {
            'src': img_element.get('src'),
            'width': int(img_element.get('width')),
            'height': int(img_element.get('height'))
        }

        # Caption
        caption_element = figure_element.find('figcaption')
        output['caption'] = caption_element.get_text(strip=True)

        return output

    def convertToJSON(self):
        data_obj = {}

        if hasattr(self, 'name'):
            data_obj['name'] = self.name
        if hasattr(self, "image"):
            data_obj["image"] = self.image
        if hasattr(self, "info_box_details"):
            data_obj["info_box_details"] = self.info_box_details
        if hasattr(self, "description"):
            data_obj["description"] = self.description
        if hasattr(self, "headings"):
            data_obj["headings"] = self.headings

        return data_obj