import feedparser
import time
from typing import Dict, List

class CachedFeed:
    """A Class that wraps feedparser to cache multiple requests to the same feed."""
    url: str
    feed: feedparser.util.FeedParserDict
    ttl: int
    last_get: float

    def __init__(self, url: str, ttl: int) -> None:
        """Initialize the class

        Args:
        url -- the url to get from
        ttl -- time to live of the cache for this url
        """
        self.url = url
        self.ttl = ttl
        self.last_get = 0

    def get(self) -> feedparser.util.FeedParserDict:
        """If ttl is not exceeded, this function will return the cached feed. Otherwise, get from the feed url and return the result.

        Returns: The feed for this url
        """
        current = time.time()
        if current - self.last_get >= self.ttl:
            self.feed = feedparser.parse(self.url)
        self.last_get = current
        return self.feed

def getCachedFeed(url: str, ttl: int) -> CachedFeed:
    """Gets a CachedFeed object for this url. This should be used instead of directly instancing the CachedFeed class to guarantee the objects get reused.

    Args:
    url -- The feed url
    ttl -- The cache time to live. Ignored if there's already a cache object for this url.
    """

    if url in cacheInstances:
        return cacheInstances[url]
    c = CachedFeed(url, ttl)
    cacheInstances[url] = c
    return c

cacheInstances: Dict[str, CachedFeed] = {}

class ManagedFeed:
    """A class to easily fetch new messages in an RSS feed."""
    cached_feed: CachedFeed
    url: str
    feed_size: int

    def __init__(self, url: str, cache_ttl: int) -> None:
        """Initialize the class.

        Args:
        url -- The url to fetch from
        cache_ttl -- How long to set the cache to live. Will be ignored if there's already a cache registered for this url.
        """
        self.url = url
        self.cached_feed = getCachedFeed(url, cache_ttl)

        try:
            self.feed_size = len(self.cached_feed.get().entries)
        except:
            raise ValueError("Couldn't get from URL")
    
    def update(self) -> List[feedparser.util.FeedParserDict]:
        """Updates the feed and returns new entries.
        
        Returns: a list of the new entries since last update
        """
        try:
            new_feed = sorted(self.cached_feed.get().entries, key=lambda k: k['published_parsed'])
        except:
            return []
        
        # feed is now empty when it wasn't before
        if len(new_feed) == 0 and self.feed_size != 0:
            return []
        
        size_diff = len(new_feed) - self.feed_size
        self.feed_size = len(new_feed)
        if size_diff == 0:
            return []
        return new_feed[-size_diff:]

