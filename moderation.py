import discord

deleteMessage = None
muted_channels_overwrites = {}






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




def is_mod(id):
    if id == 365541261156941829 or id == 287369489987928075 or id == 192322577207787523 or id == 193105896010809344 \
            or id == 207996893769236481:
        return True
    return False
