import os, time
from threading import Thread

from crawler.mde_crawler import mde_crawler
from crawler.visualizer import live_graph


class CRAWLER:
    def __init__(self, db, graph=False):
        self.running = True

        # initialize arrays
        self.active_links = db.read_table("active_links")
        self.listings_links = db.read_table("listings_links")
        self.processed_links = db.read_table("processed_links")

        # start the live graph in a separate thread
        if graph:
            graph_thread = Thread(target=live_graph, args=(self,))
            graph_thread.start()

        # start mobile.de_crawler
        self.mde_crawler_thread = Thread(target=mde_crawler, args=(self,))
        self.mde_crawler_thread.start()

    # limit graph array size
    def limit_size(self, array: list, item) -> None:
        LIST_SIZE = 200
        array.append(item)
        if len(array) == LIST_SIZE:
            array.pop(0)

    # database updater thread
    def db_sync_links(self, db) -> None:
        db.rewrite_table_values("active_links", self.active_links)
        db.rewrite_table_values("listings_links", self.listings_links)
        db.rewrite_table_values("processed_links", self.processed_links)

    # return first listing
    def listing(self):
        return self.listings_links[0]

    # stop crawler execution
    def stop(self, db):
        self.running = False
        self.db_sync_links(db)
        self.mde_crawler_thread.join()
