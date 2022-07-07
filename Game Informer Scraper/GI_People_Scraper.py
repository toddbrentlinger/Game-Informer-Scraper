import os.path
import requests
import time
import pprint
import json

from bs4 import BeautifulSoup
from GI_Person import Person

def scrapePeople():
    # Dictionary to hold Person data
    people = {}
    person_list = []

    # BeautifulSoup content
    content_staff = getBeautifulSoupContent('https://replay.fandom.com/wiki/Category:Game_Informer_staff')
    content_staff_former = getBeautifulSoupContent('https://replay.fandom.com/wiki/Category:Former_Game_Informer_staff')

    people_links_staff = content_staff.find(class_='category-page__members').find_all(class_='category-page__member-link')
    people_links_staff_former = content_staff_former.find(class_='category-page__members').find_all(class_='category-page__member-link')

    for person_link in people_links_staff:
        if person_link['title'] == 'Category:Former Game Informer staff':
            continue
        people[person_link['title']] = 'https://replay.fandom.com' + person_link['href']

    for person_link in people_links_staff_former:
        if person_link['title'] not in people:
            people[person_link['title']] = 'https://replay.fandom.com' + person_link['href']

    ## TEMP - Testing
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(people)
    #return

    for url in people.values():
        person_obj = scrapePerson(url)
        person_list.append(person_obj)
        # TEMP - Testing
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(person_obj.convertToJSON())
        return

    ## TEMP - Testing
    #person_list_json = map(lambda person: person.convertToJSON(), person_list)
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(person_list_json)
    #return

def scrapePerson(url):
    content = getBeautifulSoupContent(url)

    person_data = content.find('main')

    person_obj = Person(person_data)

    return person_obj

def getBeautifulSoupContent(url):
    response = requests.get(url, timeout=5)
    time.sleep(.5) # Wait after request to limit time between next response
    if not response:
        raise Exception("No response from:", url)
    return BeautifulSoup(response.content, "html.parser")