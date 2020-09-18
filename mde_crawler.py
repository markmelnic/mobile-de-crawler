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
        # initialize arrays
        self.active_links = []
        self.listings_urls = self.load_listings()
        self.ignored_urls = []
        self.first_request()

        # start the live graph in a separate thread
        graph_thread = threading.Thread(target=self.live_graph, args=())
        graph_thread.start()

        while True:
            with open(LISTINGS_CSV, "a", newline="") as listings_file:
                self.csv_writer = csv.writer(listings_file)
                try:
                    for url in self.active_links:
                        # skip if url has been processed already
                        if url in self.ignored_urls:
                            self.active_links.remove(url)
                            self.ignored_urls.append(url)
                        # process url and get new links
                        else:
                            self.active_links.remove(url)
                            self.ignored_urls.append(url)
                            try:
                                self.get_links(url)
                            except requests.exceptions.MissingSchema:
                                pass
                except KeyboardInterrupt:
                    pass
        graph_thread.join()

    # make the first request if there are no active links
    def first_request(self):
        response = requests.get(MDE_URL, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
        self.active_links = [
            url["href"]
            for url in soup.find_all("a", attrs={"href": re.compile("^https://")})
            if "mobile.de" in url["href"]
        ]

    # get new links 
    def get_links(self, url):
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
        for url in soup.find_all("a"):
            try:
                if "suchen.mobile.de/fahrzeuge/details.html?id" in url["href"]:
                    if not url in self.listings_urls:
                        self.csv_writer.writerow([url["href"]])
                        self.listings_urls.append(url["href"])
                elif "suchen.mobile.de" in url["href"]:
                    self.active_links.append(url["href"])
            except KeyError:
                pass

    # load indexed listings
    def load_listings(self):
        try:
            with open(LISTINGS_CSV, mode="r", newline="") as csv_file:
                csv_reader = csv.reader(csv_file)
                return list(csv_reader)
        except FileNotFoundError:
            return []

    # generate the live graph
    def live_graph(self):
        plt.style.use("dark_background")

        fig = plt.figure()
        gplot = fig.add_subplot(1, 1, 1)

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
            gplot.plot(il_history, al_history, label="Active links")
            gplot.plot(il_history, lu_history, label="Nr. of listings")
            gplot.set_title('Crawler Progress Visualizer')
            gplot.set_xlabel('Processed links')
            gplot.set_ylabel('Number of urls')
            gplot.legend()

        ani = animation.FuncAnimation(fig, animate_graph, interval=1000)
        plt.show()
