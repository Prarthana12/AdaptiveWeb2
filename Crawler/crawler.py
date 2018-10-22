from elasticsearch import Elasticsearch
import requests
class Crawler:

    def __init__(self):
        self.globalname = "Prarthana"

    def print_name(self, name: str) -> int or None:
        print("Name is ", name)
        print("Global name ", self.globalname)
        return


if __name__ == "__main__":
    es = Elasticsearch(['https://search-esaw2-s5pd4hrrxvewzfk2f6kezyg5mi.us-east-2.es.amazonaws.com/'])
    craw = Crawler()
    name = input("Enter name")
    value = craw.print_name(name)
    print(value)