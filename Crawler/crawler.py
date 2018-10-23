from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import requests
import pprint


class Crawler:
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
    es = Elasticsearch(['https://search-esaw2-s5pd4hrrxvewzfk2f6kezyg5mi.us-east-2.es.amazonaws.com/'])
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(es.info())
    craw = Crawler()
    craw.get_data("en.wikibooks.org/wiki/Java_Programming")