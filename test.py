import database, crawler


if __name__ == "__main__":
    # create database object
    database = database.DB()

    crawler = crawler.CRAWLER(database, graph=True)

    try:
        input()
    except KeyboardInterrupt:
        pass
    finally:
        crawler.stop(database)
