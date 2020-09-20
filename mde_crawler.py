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
        self.processed_urls = []
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
                        if url in self.processed_urls:
                            self.active_links.remove(url)
                            self.processed_urls.append(url)
                        # process url and get new links
                        else:
                            self.active_links.remove(url)
                            self.processed_urls.append(url)
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
                        self.active_links.append(url["href"])
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

    # limit graph array size
    def limit_size(self, array: list, item) -> None:
        LIST_SIZE = 200
        array.append(item)
        if len(array) == LIST_SIZE:
            array.pop(0)

    # generate the live graph
    def live_graph(self):
        plt.style.use("dark_background")

        fig, (links_plot, perf_plot) = plt.subplots(2)

        # timestamps = []
        # try:
        #    timestamps.append(time.time() - timestamps[-1])
        # except IndexError:
        #    timestamps.append(time.time())

        # performance plot data
        self.interval_processed = []

        # al - active links
        # pl - processed links
        # lu - listings urls
        self.al_history = []
        self.pl_history = []
        self.lu_history = []

        def animate(i):
            # links plot
            self.limit_size(self.al_history, len(self.active_links))
            self.limit_size(self.pl_history, len(self.processed_urls))
            self.limit_size(self.lu_history, len(self.listings_urls))

            links_plot.clear()
            links_plot.plot(
                self.pl_history, self.al_history, label="Active links", color="#f4a261"
            )
            links_plot.plot(
                self.pl_history,
                self.lu_history,
                label="Nr. of listings",
                color="#2a9d8f",
            )
            links_plot.set_title("Crawler Progress Visualizer")
            links_plot.set_xlabel("Processed links")
            links_plot.set_ylabel("Number of urls")
            links_plot.legend()

            # performance plot
            try:
                self.limit_size(
                    self.interval_processed, self.pl_history[-1] - self.pl_history[-2]
                )
            except IndexError:
                self.limit_size(self.interval_processed, 0)
            perf_plot.clear()
            perf_plot.plot(
                self.pl_history,
                self.interval_processed,
                label="Interval",
                color="#e9c46a",
            )
            perf_plot.set_title("Crawler performance")
            perf_plot.set_xlabel("Number of processed links")
            perf_plot.set_ylabel("Processed per iterations")
            perf_plot.legend()

        anim = animation.FuncAnimation(fig, animate, interval=1000)
        plt.show()


if __name__ == "__main__":
    crawler = MDE_CRAWLER()
