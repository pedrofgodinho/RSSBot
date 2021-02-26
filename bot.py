from rssmanager import ManagedFeed
from guild_manager import GuildManager

import random

import discord
from discord.utils import get
from discord.ext import tasks
import pickle

from emoji import UNICODE_EMOJI

from datetime import datetime

import os
from dotenv import load_dotenv

# Keys are the guild id for each active guild, values are GuildManagers for them
load_dotenv('.env')
TOKEN = os.getenv('DISCORD_TOKEN')
guilds = {}
client = discord.Client()

help_message = '''
Usage:
!rss add <role name> <emoji> <rss url>
!rss remove <role name>
!rss status
'''


@client.event
async def on_ready():
    update.start()


@client.event
async def on_message(message):
    # Add the guild to guilds dict if it isn't being tracked yet
    if message.guild is None:
        return
    guild_id = message.guild.id
    if guild_id not in guilds:
        guilds[guild_id] = GuildManager(guild_id)
    
    # Ignore messages from bot itself
    if message.author == client.user:
        return

    # Only listen to messages starting with !rss
    if message.content.startswith('!rss'):

        # Split arguments
        split = message.content.split(' ')
        if len(split) == 1:
            await message.channel.send(help_message)
            return

        command = split[1]
        args = split[2:]

        # Management commands
        if message.channel.id == guilds[guild_id].management_channel_id:
            if command == 'add':
                if len(args) < 3:
                    await message.channel.send('Not enough arguments. See !rss')
                    return
                
                                
                if not is_emoji(args[1]):
                    await message.channel.send('Second argument needs to be an emoji.')
                    return
                
                if args[1] in guilds[guild_id].watching_emoji.values():
                    await message.channel.send('Emoji already in use.')
                    return

                # Create role if it doesn't exist
                if not get(message.guild.roles, name=args[0]):
                    await message.guild.create_role(name=args[0], colour=discord.Colour(random.randint(0, 0xffffff)))
                    await message.channel.send(f'Created role {get(message.guild.roles, name=args[0]).mention}.')

                # Add feed to guild manager
                if not guilds[guild_id].add_feed(get(message.guild.roles, name=args[0]).id, args[1], args[2]):
                    await message.channel.send(f'Could not add {args[2]}! Make sure it is a valid RSS feed url.')
                    await get(message.guild.roles, name=args[0]).delete()
                    return
                await message.channel.send(f'Assigned rss feed {args[2]} to {get(message.guild.roles, name=args[0]).mention}!')

                if guilds[guild_id].subscription_message_id is not None:
                    await update_subscription_message(guilds[guild_id], emoji_to_add=args[1])

                save()
                return
            elif command == 'remove':
                if len(args) < 1:
                    await message.channel.send('Not enough arguments. See !rss')
                    return
                
                role = get(message.guild.roles, name=args[0])
                # If role doesn't exist
                if role is None:
                    await message.channel.send(f'Role {args[0]} does not exist!')
                    return

                # If role has no feed assigned
                if not guilds[guild_id].has_feed(role.id):
                    await message.channel.send(f'No feed assigned to {role.mention}.')
                    return

                emoji = guilds[guild_id].watching_emoji[role.id]
                # Remove role
                guilds[guild_id].remove_feed(role.id)
                await role.delete()

                await message.channel.send(f'Removed feed for role {role.name}!')

                if guilds[guild_id].subscription_message_id is not None:
                    await update_subscription_message(guilds[guild_id], emoji_to_remove=emoji)
                return
            elif command == 'cheat': # TEMP
                for watched in guilds[guild_id].watching:
                    guilds[guild_id].watching[watched].feed_size = max(0, guilds[guild_id].watching[watched].feed_size - 1)
                return
            elif command == 'status':
                to_send = 'Status:'
                for watched in guilds[guild_id].watching:
                    to_send += f'\n{get(message.guild.roles, id=watched).mention} is watching {guilds[guild_id].watching[watched].url} (currently {guilds[guild_id].watching[watched].feed_size} entries)'
                await message.channel.send(to_send)
                return
            else:
                await message.channel.send(help_message)
                return

        # Administrator only commands
        if message.author.guild_permissions.administrator:
            if command == 'manage_here':
                guilds[guild_id].management_channel_id = message.channel.id
                await message.channel.send('Using this channel as management channel!')
                save()
                return
            elif command == 'notify_here':
                guilds[guild_id].notification_channel_id = message.channel.id
                await message.channel.send('Using this channel as notification channel!')
                save()
                return
            elif command == 'subscribe_here':
                await message.channel.send('Using this channel as subscription channel!')
                await change_subscription_channel(guilds[guild_id], message.channel)
                save()
                return
            elif command == 'clean':
                del guilds[guild_id]
                return
            else:
                await message.channel.send('Start by setting up a management channel with `!rss manage_here`. You should then setup a notifications server with `!rss notify_here` and a subscription channel with `!rss subscribe_here`.')


@client.event
async def on_raw_reaction_add(payload):
    for guild_id in guilds:
        if payload.channel_id == guilds[guild_id].subscription_channel_id and payload.message_id == guilds[guild_id].subscription_message_id:
            for role_id in guilds[guild_id].watching_emoji:
                if payload.emoji.name == guilds[guild_id].watching_emoji[role_id]:
                    role = get(client.get_guild(guild_id).roles, id=role_id)
                    await payload.member.add_roles(role)
                    return
            return


@client.event
async def on_raw_reaction_remove(payload):
    for guild_id in guilds:
        if payload.channel_id == guilds[guild_id].subscription_channel_id and payload.message_id == guilds[guild_id].subscription_message_id:
            for role_id in guilds[guild_id].watching_emoji:
                if payload.emoji.name == guilds[guild_id].watching_emoji[role_id]:
                    role = get(client.get_guild(guild_id).roles, id=role_id)
                    member = await client.get_guild(guild_id).fetch_member(payload.user_id)
                    await member.remove_roles(role)
                    return
            return


@tasks.loop(minutes=5)
async def update():
    log('Updating...')
    num_updates = 0
    changed = False
    for guild_id in guilds:
        if guilds[guild_id].notification_channel_id is not None:
            for role_id in guilds[guild_id].watching:
                updates = guilds[guild_id].watching[role_id].update()
                if updates:
                    num_updates += 1
                    changed = True
                    for update in updates:
                        guild = client.get_guild(guild_id)
                        role = get(guild.roles, id=role_id)
                        embed = discord.Embed(
                            title=update['title'], 
                            url=update['links'][0]['href'],
                            description=f'New update in {role.mention}.',
                            color=role.colour
                        )
                        try:
                            await guild.get_channel(guilds[guild_id].notification_channel_id).send(content=role.mention, embed=embed)
                        except:
                            log(f'Exception on guild with id {guild_id}')
                            log(sys.exc_info()[0])
    if changed:
        save()
    log(f'Found new messages in {num_updates} feeds.')
    log('Update Finished.')


async def change_subscription_channel(guild_manager, channel):
    guild_manager.subscription_channel_id = channel.id

    message = 'React to subscribe to notifications from the following channels:\n'
    for role_id in guild_manager.watching_emoji:
        message += f'{guild_manager.watching_emoji[role_id]} - {get(client.get_guild(guild_manager.guild_id).roles, id=role_id).mention}\n'
    sent = await channel.send(message)
    guild_manager.subscription_message_id = sent.id

    for role_id in guild_manager.watching_emoji:
        await sent.add_reaction(guild_manager.watching_emoji[role_id])


async def update_subscription_message(guild_manager, emoji_to_add=None, emoji_to_remove=None):
    message = 'React to subscribe to notifications from the following channels:\n'
    for role_id in guild_manager.watching_emoji:
        message += f'{guild_manager.watching_emoji[role_id]} - {get(client.get_guild(guild_manager.guild_id).roles, id=role_id).mention}\n'

    subscription_message = await client.get_guild(guild_manager.guild_id).get_channel(guild_manager.subscription_channel_id).fetch_message(guild_manager.subscription_message_id)
    await subscription_message.edit(content=message)

    if emoji_to_add is not None:
        await subscription_message.add_reaction(emoji_to_add)
    if emoji_to_remove is not None:
        for reaction in subscription_message.reactions:
            if reaction.emoji == emoji_to_remove:
                await reaction.clear()


def is_emoji(s):
    count = 0
    for emoji in UNICODE_EMOJI['en']:
        count += s.count(emoji)
        if count > 1:
            return False
    return bool(count)


def save():
    with open('pickle', 'wb') as fd:
        pickle.dump(guilds, fd)


def log(message):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {message}')


try:
    print('Loading from pickle')
    with open('pickle', 'rb') as fd:
        guilds = pickle.load(fd)
except FileNotFoundError as e:
    print('No pickle found, starting with no data')

client.run(TOKEN)
