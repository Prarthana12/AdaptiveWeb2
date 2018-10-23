from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import requests
import pprint
import os


class Crawler:
    def __init__(self):
        self.esurl = os.environ.get('ESCONN')

    def get_data(self,url):
        r = requests.get("http://" + url)
        count = 0
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        for link in soup.find_all('a'):
            if "Java_Programming" in str(link.get('href')):
                print(link.get('href'))
                count+=1
        print("No of links{0}sdv jsh{1}".format(count, "radsfs"))


if __name__ == "__main__":
    craw = Crawler()
    es = Elasticsearch([craw.esurl])
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(es.info())

    craw.get_data("en.wikibooks.org/wiki/Java_Programming")