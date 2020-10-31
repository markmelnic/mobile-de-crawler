import os, time, threading

from crawler.mde_crawler import mde_crawler
from crawler.visualizer import live_graph

class CRAWLER:
    def __init__(self, db):
        # initialize arrays
        self.active_links = db.read_table("active_links")
        self.listings_links = db.read_table("listings_links")
        self.processed_links = db.read_table("processed_links")

        # start the database updater thread
        self.running = True
        db_thread = threading.Thread(target=self.database_updater, args=(db, ))
        db_thread.start()

        # start the live graph in a separate thread
        graph_thread = threading.Thread(target=live_graph, args=(self, ))
        graph_thread.start()

        # start mobile.de_crawler
        mde_crawler_thread = threading.Thread(target=mde_crawler, args=(self, ))
        mde_crawler_thread.start()

        try:
            while True:
                stopper = input("Type S or STOP to interrupt the execution.\n")
                if "s" in stopper.lower():
                    raise KeyboardInterrupt
        except KeyboardInterrupt:
            print("Interruption detected, this might take up to 45 seconds.")
            self.running = False
            mde_crawler_thread.join()
            db_thread.join()
            os._exit(0)

    # turn list into tuples
    def tuplify(self, data: list):
        return [(d,) for d in data]

    # limit graph array size
    def limit_size(self, array: list, item) -> None:
        LIST_SIZE = 200
        array.append(item)
        if len(array) == LIST_SIZE:
            array.pop(0)

    # database updater thread
    def database_updater(self, db) -> None:
        while True:
            time.sleep(60)
            db.rewrite_table_values("active_links", self.tuplify(self.active_links))
            db.rewrite_table_values("listings_links", self.tuplify(self.listings_links))
            db.rewrite_table_values("processed_links", self.tuplify(self.processed_links))
            if self.running == False:
                break
