from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import requests
import pprint
import os
import json


class Crawler:
    def __init__(self):
        self.esurl = os.environ.get('ESCONN')
        self.baseURL = "http://en.wikibooks.org"
        self.list_of_all_links = []

    def start_crawler(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                main_page_content = response.content
                self.list_of_all_links = self.get_links_on_page(
                    main_page_content)
                print(self.list_of_all_links)
                return True
            else:
                print("Couldn't read the page! Make sure the URL is correct!")
                return False
        except Exception as e:
            print(e)

    def get_links_on_page(self, main_page_content):
        all_links = []
        soup = BeautifulSoup(main_page_content, 'html.parser')
        try:
            contents = soup.find('div', {'id': 'mw-content-text'})
            unordered_lists = contents.findAll('ul')
            for ul in unordered_lists:
                list_item = ul.findAll('li')
                for li in list_item:
                    all_links.append(
                        self.baseURL + li.findAll('a')[-1]['href'])
        except Exception as e:
            print(e)
        return all_links[6:]

    def get_content_from_all_links(self):

        while self.list_of_all_links != []:
            current_link = self.list_of_all_links.pop(0)
            response = requests.get(current_link)
            if response.status_code == 200:
                current_page_content = response.content
                self.get_content_from_each_link(current_link,
                                                current_page_content)
                return True
            else:
                return False

    def get_content_from_each_link(self, current_link, current_page_content):
        soup = BeautifulSoup(current_page_content, 'html.parser')
        main_div = soup.find('div', {'class': 'mw-parser-output'}).find(
            'p').next_siblings
        page_title = soup.find('h1').text
        sub_title = ''
        content_in_tag = ''
        content_type = ''
        print('parsing page: {}'.format(page_title))
        for sibling in main_div:
            content_dict = {}
            if sibling.name == 'h2':
                sub_title = sibling.text
            elif sibling.name == 'p' or sibling.name == 'ul' or sibling.name == 'pre':
                content_in_tag = sibling.text
                content_type = 'text'
            elif sibling.name != None and sibling.find('div', {
                    'class': 'mw-highlight mw-content-ltr'}) is not None:
                content_in_tag = sibling.find('div', {
                    'class': 'mw-highlight mw-content-ltr'}).find('pre').text
                content_type = 'code'
            else:
                continue
            content_dict['pageURL'] = current_link
            content_dict['pageTitle'] = page_title
            content_dict['contentHeader'] = sub_title
            content_dict['content'] = content_in_tag
            content_dict['contentType'] = content_type
            data = json.dumps(content_dict)
            print(data)


if __name__ == "__main__":
    craw = Crawler()
    es = Elasticsearch([craw.esurl])
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(es.info())

    got_links = craw.start_crawler("http://en.wikibooks.org/wiki/Java_Programming")
    if got_links:
        got_content = craw.get_content_from_all_links()
        if got_content:
            print("Successfully got content from all links.")
        else:
            print("Couldn't get ")
    else:
        print("Couldn't get the links on the page")
