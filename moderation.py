import discord

coned = {}
deleteMessage = None
muted_channels_overwrites = {}


async def uncone(message):
    mentions = message.mentions
    for user in mentions:
        if user.id in coned:
            try:
                await user.edit(nick=coned.get(user.id, None))
            except discord.Forbidden:
                print("Can't change nickname")
            del coned[user.id]
            await message.channel.send(user.mention + " unconed")
        else:
            await message.channel.send(user.mention + " wasn't coned")
    return


async def cone(message):
    mentions = message.mentions
    for user in mentions:
        if user.nick is None:
            coned[user.id] = user.name
        else:
            coned[user.id] = user.nick
        try:
            await user.edit(nick="CONE OF SHAME!")
        except discord.Forbidden:
            print("Can't change nickname")
        await message.channel.send("Shame on you! " + user.mention)
    return


def is_coned(user_id):
    return user_id in coned


async def cone_message(message):
    await message.add_reaction("\U0001F4A9")
    await message.add_reaction("\U0001F1F8")
    await message.add_reaction("\U0001F1ED")
    await message.add_reaction("\U0001F1E6")
    await message.add_reaction("\U0001F1F2")
    await message.add_reaction("\U0001F1EA")


async def get_coned(message):
    msg = ""
    for user in coned:
        msg = msg + coned.get(user, "") + " "
    if msg != "":
        await message.channel.send(msg)
    else:
        await message.channel.send("Currently none")
    return


async def mute(message):
    mentions = message.mentions
    for user in mentions:
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        await message.channel.set_permissions(user, overwrite=overwrite)
        await message.channel.send(user.mention + " has been silenced")
    return


async def unmute(message):
    mentions = message.mentions
    for user in mentions:
        await message.channel.set_permissions(user, overwrite=None)
        await message.channel.send(user.mention + " has been forgiven")
    return


async def server_mute(message):
    mentions = message.mentions
    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = False
    overwrite.speak = False
    channels = message.guild.channels
    for user in mentions:
        for channel in channels:
            await channel.set_permissions(user, overwrite=overwrite)
        await message.channel.send("You're annoying " + user.mention)
    return


async def server_unmute(message):
    mentions = message.mentions
    channels = message.guild.channels
    for user in mentions:
        for channel in channels:
            await channel.set_permissions(user, overwrite=None)
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
        if not overwrite[1].manage_messages and overwrite[1].send_messages is not False:
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
