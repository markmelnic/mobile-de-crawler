import crawler


if __name__ == "__main__":
    # create database object
    database = crawler.DB()

    crawler = crawler.CRAWLER(database)
