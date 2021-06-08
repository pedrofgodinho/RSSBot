from rssmanager import ManagedFeed
from typing import Dict

class GuildManager:
    """A class that holds variables related to each guild the bot is on"""
    guild_id: int = None
    management_channel_id: int = None
    notification_channel_id: int = None
    subscription_channel_id: int = None
    subscription_message_id: int = None
    watching: Dict[id, ManagedFeed] = {}
    watching_emoji: Dict[id, str] = {}

    def __init__(self, guild_id: int):
        """ Initializes the class

        Args:
        guild_id -- The id of the guild this object manages
        """
        self.guild_id = guild_id
    
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

