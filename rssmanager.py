import feedparser
import hashlib
import time

class ManagedFeed:
    def __init__(self, url):
        self.url = url
        self.feed = []
        try:
            new_feed = sorted(feedparser.parse(url).entries[::-1], key=lambda k: k['published_parsed'])
            for i in new_feed:
                self.feed.append(self.encodeFeed(i))
        except:
            raise ValueError("Invalid URL")
    
    def encodeFeed(self, i):
        hash_object = hashlib.sha1(i['summary_detail']['value'].encode())
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def update(self):
        try:
            new_feed = sorted(feedparser.parse(self.url).entries[::-1], key=lambda k: k['published_parsed'])
        except:
            return []
        size_diff = len(new_feed) - len(self.feed)
        if size_diff <= 0:
            return []
        else:
            for i in new_feed[-size_diff:]:
                self.feed.append(self.encodeFeed(i))

        return new_feed[-size_diff:]

    def findDiff(self):
        diffFeed = self.update()
        new_feed = sorted(feedparser.parse(self.url).entries[::-1], key=lambda k: k['published_parsed'])
        hashedFeed = [self.encodeFeed(i) for i in new_feed]
        for k in range(len(self.feed)):
            if(self.feed[k]!=hashedFeed[k]):
                diffFeed.append(new_feed[k])
        return diffFeed
