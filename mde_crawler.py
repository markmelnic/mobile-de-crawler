import re, csv, time, requests, threading
from bs4 import BeautifulSoup

import matplotlib.pyplot as plt
import matplotlib.animation as animation

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

        graph_thread = threading.Thread(target=self.live_graph, args=())
        graph_thread.start()

        while True:
            with open(LISTINGS_CSV, "a", newline="") as listings_file:
                self.csv_writer = csv.writer(listings_file)
                try:
                    for url in self.active_links:
                        if url in self.ignored_urls:
                            self.active_links.remove(url)
                            self.ignored_urls.append(url)
                        else:
                            self.active_links.remove(url)
                            self.ignored_urls.append(url)
                            try:
                                self.get_links(url)
                            except requests.exceptions.MissingSchema:
                                pass
                except KeyboardInterrupt:
                    graph_thread.join()
                    pass

    def first_request(self):
        response = requests.get(MDE_URL, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
        self.active_links = [
            url["href"]
            for url in soup.find_all("a", attrs={"href": re.compile("^https://")})
            if "mobile.de" in url["href"]
        ]

    def get_links(self, url):
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
        for url in soup.find_all("a"):
            try:
                if "suchen.mobile.de/fahrzeuge/details.html?id" in url["href"]:
                    self.csv_writer.writerow([url["href"]])
                    self.listings_urls.append(url["href"])
                elif "suchen.mobile.de" in url["href"]:
                    self.active_links.append(url["href"])
            except KeyError:
                pass

    def load_listings(self):
        with open(LISTINGS_CSV, mode="r", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            return list(csv_reader)

    def live_graph(self):
        fig = plt.figure()
        gplot = fig.add_subplot(1,1,1)
        plt.style.use('seaborn-darkgrid')

        # al - active links
        # lu - listings urls
        # il - ignored links
        al_history = []
        il_history = []
        lu_history = []

        def animate_graph(i):
            al_history.append(len(self.active_links))
            il_history.append(len(self.ignored_urls))
            lu_history.append(len(self.listings_urls))

            gplot.clear()
            gplot.plot(il_history, al_history, label="Active")
            gplot.plot(il_history, il_history, label="Ignored")
            gplot.plot(il_history, lu_history, label="Listings")
            gplot.legend()

        ani = animation.FuncAnimation(fig, animate_graph, interval=1000)
        plt.show()
