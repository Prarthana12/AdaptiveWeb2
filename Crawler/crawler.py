from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import requests
import pprint
import os
import json
import certifi


class Crawler:
    def __init__(self):
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
            else:
                flag = False
        return flag

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
            craw = Crawler()
            craw.es_index_doc(data)

    def es_create_index(self):
        pPrint = pprint.PrettyPrinter(indent=4)
        try:
            esUrl = "https://search-esaw2-s5pd4hrrxvewzfk2f6kezyg5mi.us-east-2.es.amazonaws.com/"
            esClient = Elasticsearch([esUrl], use_ssl=True, verify_certs=True, ca_certs=certifi.where())
            pPrint.pprint("Connected {0}".format(esClient.info()))
            indexExist = esClient.indices.exists('aw2')
            body = '''{
                          "settings": {
                            "number_of_shards": 2,
                            "analysis": {
                              "analyzer": {
                                "default": {
                                  "type": "custom",
                                  "tokenizer": "standard",
                                  "filter": [
                                    "lowercase",
                                    "keyword_repeat",
                                    "porter_stem",
                                    "unique_stem",
                                    "stopFilter"
                                  ]
                                }
                              },
                              "filter": {
                                "stopFilter": {
                                  "type": "stop",
                                  "stopwords": "_english_"
                                },
                                "unique_stem": {
                                  "type": "unique",
                                  "only_on_same_position": true
                                }
                              }
                            }
                          },
                          "mappings": {
                            "crawledData": {
                              "properties": {
                                "pageURL": {
                                  "type": "text"
                                },
                                "pageTitle": {
                                  "type": "text"
                                },
                                "contentHeader": {
                                  "type": "text"
                                },
                                "content": {
                                  "type": "text",
                                  "analyzer": "default"
                                },
                                "contentType": {
                                  "type": "text"
                                }
                              }
                            }
                          }
                        }'''
            if indexExist:
                esClient.indices.delete(index='aw2', ignore=[400, 404])
                print("Index deleted")
            esClient.indices.create(index='aw2', body=body)
            print("Index created")
        except Exception as ex:
            pPrint.pprint("Error: {0}".format(ex))

    def es_index_doc(self, data):
        pPrint = pprint.PrettyPrinter(indent=4)
        try:
            esUrl = "https://search-esaw2-s5pd4hrrxvewzfk2f6kezyg5mi.us-east-2.es.amazonaws.com/"
            esClient = Elasticsearch([esUrl], use_ssl=True, verify_certs=True, ca_certs=certifi.where())
            esClient.index(index='aw2', doc_type='crawledData', body=data)
        except Exception as ex:
            pPrint.pprint("Error: {0}".format(ex))


if __name__ == "__main__":
    craw = Crawler()
    craw.es_create_index()
    pp = pprint.PrettyPrinter(indent=4)
    got_links = craw.start_crawler("http://en.wikibooks.org/wiki/Java_Programming")
    if got_links:
        got_content = craw.get_content_from_all_links()
        if got_content:
            print("Successfully got content from all links.")
        else:
            print("Couldn't get ")
    else:
        print("Couldn't get the links on the page")
