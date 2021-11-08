from __future__ import annotations
from operator import contains

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
import time

URL_BASE = "https://iwaspoisoned.com"
PAGE_QUERY = "/?page="
PAGE_NUMBER = 1
RESULT = []

def connect_to_website():
    response = requests.get(URL_BASE + PAGE_QUERY + str(PAGE_NUMBER))
    html_soup = BeautifulSoup(response.content, "html.parser")
    return html_soup

def scraping_info(html_soup):
    info_container = html_soup.find_all("div", {"class": "report-title"})
    for i in range(len(info_container)):
        info_of_place = {}
        info_of_place["name"] = info_container[i].h2.text.split(",")[0]
        info_of_place["location"] = info_container[i].h2.text.split(",")[2]
        info_of_place["last_updated"] = info_container[i].h3.text
        RESULT.append(info_of_place)
    
    return RESULT

def scraping_symptons(html_soup):
    RESULT = scraping_info(html_soup)
    sympton_container = html_soup.find_all("div", class_="card-body p-0")
    for i in range(len(sympton_container)):
        RESULT[i]["symptons"] = sympton_container[i].blockquote.text.replace(" ", "").split(":")[1].split("See")[0].split(",")

    return RESULT

def main():
    t = time.process_time()
    container = connect_to_website()
    result = scraping_symptons(container)
    print(time.process_time() - t)
    return result


#if __name__ == "__main__":
#    main()