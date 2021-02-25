from rssmanager import ManagedFeed

# A class to each Guild's watched rss feeds
class GuildManager:
    def __init__(self, guild_id):
        # The id of the guild
        self.guild_id = guild_id
        # The id of the management channel
        self.management_channel_id = None
        # The id of the message channel
        self.notification_channel_id = None
        # The id of the subscription channel
        self.subscription_channel_id = None
        # The id of the subscription message
        self.subscription_message_id = None
        # Watching keys are the role id and the value is the ManagedFeed being watched by that role
        self.watching = {}
        self.watching_emoji = {}
    
    def add_feed(self, role_id, emoji, url):
        try:
            feed = ManagedFeed(url)
            self.watching[role_id] = feed
            self.watching_emoji[role_id] = emoji
            return True
        except ValueError as e:
            return False
    

    def has_feed(self, role_id):
        return role_id in self.watching
    

    def remove_feed(self, role_id):
        del self.watching[role_id]
        del self.watching_emoji[role_id] 

