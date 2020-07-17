import sys
from pymongo import MongoClient
from NewspaperScraper import *

client = MongoClient()
db = client.News_database


def run_scraper (scraper):
    scraper.get_pages()
    data = scraper.newspaper_parser()
    scraper.write_to_csv(data, "data.csv")


def initialize_scraper (args):

        run_scraper(WSJScraper("Wall Street Journal", "PRO BANKRUPTCY","2020-07-06","2020-07-07","", ""))



if __name__ == "__main__":
    initialize_scraper(sys.argv)
