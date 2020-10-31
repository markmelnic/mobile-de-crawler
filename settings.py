# requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
}

# database settings
CRAWLER_DB = "crawler.sqlite3"
TABLES = [
    ("listings_links", [("links", "text")]),
    ("processed_links", [("links", "text")]),
    ("active_links", [("links", "text")]),
]
