import feedparser

class ManagedFeed:
    def __init__(self, url):
        self.url = url
        try:
            self.feed_size = len(sorted(feedparser.parse(url).entries[::-1], key=lambda k: k['published_parsed']))
        except:
            raise ValueError("Invalid URL")
    
    def update(self):
        try:
            new_feed = sorted(feedparser.parse(self.url).entries[::-1], key=lambda k: k['published_parsed'])
        except:
            return []
        
        # Assume rss feed is down
        if len(new_feed) == 0 and self.feed_size != 0:
            return []
        
        size_diff = len(new_feed) - self.feed_size
        self.feed_size = len(new_feed)
        if size_diff == 0:
            return []
        return new_feed[-size_diff:]

