from rssmanager import ManagedFeed
from typing import Dict

class GuildManager:
    """A class that holds variables related to each guild the bot is on"""
    
    def __init__(self, guild_id: int):
        """ Initializes the class

        Args:
        guild_id -- The id of the guild this object manages
        """
        self.guild_id: int = guild_id
        self.management_channel_id: int = None
        self.notification_channel_id: int = None
        self.subscription_channel_id: int = None
        self.subscription_message_id: int = None
        self.watching: Dict[id, ManagedFeed] = {}
        self.watching_emoji: Dict[id, str] = {}

    
    def add_feed(self, role_id: int, emoji: str, url: str) -> None:
        """Adds a feed to be watched by the server

        Args:
        role_id -- The id of the role watching this feed
        emoji -- The subscription emoji for this role
        url -- The feed url
        """
        try:
            feed = ManagedFeed(url, 180)
            self.watching[role_id] = feed
            self.watching_emoji[role_id] = emoji
            return True
        except ValueError:
            return False
    

    def has_feed(self, role_id: int) -> bool:
        """Returns whether a role is watching a feed"""
        return role_id in self.watching
    

    def remove_feed(self, role_id: int) -> None:
        """Removes a feed being watched by a role"""
        del self.watching[role_id]
        del self.watching_emoji[role_id] 

