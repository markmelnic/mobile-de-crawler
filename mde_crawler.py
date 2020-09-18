import re, csv, requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
}
MDE_URL = "https://www.mobile.de/"
LISTINGS_CSV = "listings.csv"


class MDE_CRAWLER:
    def __init__(self):
        self.active_links = []
        self.listings_urls = []
        self.ignored_urls = []
        self.first_request()

        while True:
            with open(LISTINGS_CSV, "a", newline="") as listings_file:
                self.csv_writer = csv.writer(listings_file)
                try:
                    for url in self.active_links:
                        if url in self.ignored_urls:
                            self.active_links.remove(url)
                            self.ignored_urls.append(url)
                        else:
                            print("Tree size =", len(self.active_links))
                            self.active_links.remove(url)
                            self.ignored_urls.append(url)
                            try:
                                self.get_links(url)
                            except requests.exceptions.MissingSchema:
                                pass
                except KeyboardInterrupt:
                    pass

    def first_request(self):
        response = requests.get(MDE_URL, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
        self.active_links = [
            url["href"]
            for url in soup.find_all("a", attrs={"href": re.compile("^https://")})
            if "mobile.de" in url["href"]
        ]
