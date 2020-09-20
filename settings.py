
# database settings
CRAWLER_DB = "crawler.sqlite3"
TABLES = [
        ("listings_links", [("links", "text")]),
        ("processed_links", [("links", "text")]),
        ("active_links", [("links", "text")])
]
