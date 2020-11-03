import db, crawler


if __name__ == "__main__":
    # create database object
    database = db.DB()

    crawler = crawler.CRAWLER(database)
