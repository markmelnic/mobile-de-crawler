import re, requests
from bs4 import BeautifulSoup

from settings import HEADERS

MDE_URL = "https://www.mobile.de/"


def mde_crawler(crawler):
    while True:
        if crawler.active_links == []:
            first_request(crawler)
        for url in crawler.active_links:
            # skip if url has been processed already
            if url in crawler.processed_links:
                crawler.active_links.remove(url)
                crawler.processed_links.append(url)
            # process url and get new links
            else:
                crawler.active_links.remove(url)
                crawler.processed_links.append(url)
                try:
                    get_links(crawler, url)
                except requests.exceptions.MissingSchema:
                    pass

            if crawler.running == False:
                break
        if crawler.running == False:
            break


# make the first request if there are no active links
def first_request(crawler):
    response = requests.get(MDE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [
        url["href"]
        for url in soup.find_all("a", attrs={"href": re.compile("^https://")})
        if "mobile.de" in url["href"]
    ]
    for link in links:
        crawler.active_links.append(link)


# get new links
def get_links(crawler, url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    for url in soup.find_all("a"):
        try:
            if "suchen.mobile.de/fahrzeuge/details.html?id" in url["href"]:
                if not url in crawler.listings_links:
                    crawler.listings_links.append(url["href"])
                    crawler.active_links.append(url["href"])
            elif "suchen.mobile.de" in url["href"]:
                crawler.active_links.append(url["href"])
        except KeyError:
            pass
