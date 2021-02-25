from rssmanager import ManagedFeed
from guild_manager import GuildManager
import pickle

def save(guilds, filename):
    with open(filename, 'wb') as fd:
        pickle.dump(guilds, fd)

def load(filename):
    with open(filename, 'rb') as fd:
        return pickle.load(fd)

def list_guilds(guilds):
    print('Currently tracking guilds with ids:')
    for key in guilds:
        print(key)
    print()

def list_feeds(guilds, guild_id):
    print(f'In guild with id {guild_id} the following feeds are being watched:')
    for key in guilds[guild_id].watching:
        print(f'Role with id {key} is watching {guilds[guild_id].watching[key].url} ({guilds[guild_id].watching[key].feed_size} entries)')

if __name__ == '__main__':
    guilds = load('pickle')
    list_guilds(guilds)