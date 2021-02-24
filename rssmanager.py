import feedparser

class ManagedFeed:
    def __init__(self, url):
        self.url = url
        try:
            self.feed = sorted(feedparser.parse(url).entries[::-1], key=lambda k: k['published_parsed'])
        except:
            raise ValueError("Invalid URL")
    
    def update(self):
        try:
            new_feed = sorted(feedparser.parse(self.url).entries[::-1], key=lambda k: k['published_parsed'])
        except:
            return []
        size_diff = len(new_feed) - len(self.feed)
        self.feed = new_feed
        if size_diff == 0:
            return []
        return new_feed[-size_diff:]

