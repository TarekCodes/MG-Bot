import discord

coned = {}


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
