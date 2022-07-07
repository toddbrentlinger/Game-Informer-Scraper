import pprint

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
            imageObject["width"] = image_element.get('width')
            imageObject["height"] = image_element.get('height')
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
            label = detail_element.find(class_='pi-data-label').get_text(strip=True)
            
            value_element = detail_element.find(class_='pi-data-value')
            value_anchor_link = value_element.find('a')
            if value_anchor_link is not None:
                value = {
                    'href': value_anchor_link.get('href'),
                    'text': value_anchor_link.get_text(strip=True)
                }
            else:
                value = value_element.get_text(strip=True)
            self.info_box_details[label] = value

        # First child is 'p' element that holds info box info.
        # Start with second child
        child = list(main_content.children)[1]

        # Description
        # Get all 'p' elements until reaching stop or end
        self.description = []
        while child.name not in ('h2', 'h3', 'table'):
            if child.name is not None and child.name == 'p':
                child_text = child.get_text().replace('\n', '')
                if child_text:
                    self.description.append(' '.join([text for text in child.stripped_strings]))
            child = child.next_sibling
        # Skip Replay Appearance AND Super Replay Appearances
        return

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

        return data_obj