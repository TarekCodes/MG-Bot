import discord

deleteMessage = None
muted_channels_overwrites = {}


async def server_mute(message):
    mentions = message.mentions
    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = False
    overwrite.speak = False
    channels = message.guild.channels
    for user in mentions:
        for channel in channels:
            try:
                await channel.set_permissions(user, overwrite=overwrite)
            except Exception as e:
                print(e)
        await message.channel.send("You're annoying " + user.mention)
    return


async def server_unmute(message):
    mentions = message.mentions
    channels = message.guild.channels
    for user in mentions:
        for channel in channels:
            try:
                await channel.set_permissions(user, overwrite=None)
            except Exception as e:
                print(e)
        await message.channel.send("Better not do it again " + user.mention)
    return


async def clear(message):
    try:
        parsed = message.content.split()
        global deleteMessage
        deleteMessage = message
        deleted = await message.channel.purge(limit=int(parsed[1]), check=is_person)
        await message.channel.send('Deleted {} message(s)'.format(len(deleted)))
    except Exception as e:
        await message.channel.send("Invalid Command")
    return


async def mute_channel(message):
    channel = message.channel
    overwrites = channel.overwrites
    muted_channels_overwrites[message.channel.name] = overwrites
    for overwrite in overwrites:
        if not is_mod(overwrite[0].id) and overwrite[1].send_messages is not False:
            cant_send = discord.PermissionOverwrite()
            cant_send.send_messages = False
            await channel.set_permissions(overwrite[0], overwrite=cant_send)
    await message.channel.send("YOU SHALL NOT CHAT!")


async def unmute_channel(message):
    channel = message.channel
    if channel.name not in muted_channels_overwrites:
        await message.channel.send("Channel wasn't muted")
        return
    overwrites = muted_channels_overwrites[channel.name]
    for overwrite in overwrites:
        await channel.set_permissions(overwrite[0], overwrite=overwrite[1])
    del muted_channels_overwrites[channel.name]
    await message.channel.send("CHAT YOU FOOLS!")


def is_person(m):
    mentions = deleteMessage.mentions
    if len(mentions) == 0:
        return True
    return m.author == deleteMessage.mentions[0]


def is_mod(id):
    if id == 365541261156941829 or id == 287369489987928075 or id == 192322577207787523 or id == 193105896010809344 \
            or id == 207996893769236481:
        return True
    return False
