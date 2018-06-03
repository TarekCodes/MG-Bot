import config
import dynamo
import discord

TOKEN = config.botToken
coned = {}
welcomeChat = 334014732572950528
announcementsChat = 349679027126272011
rulesChat = 365624761398591489
deleteMessage = None
modCommands = ["$uncone ", "$cone ", "$who", "$mute ", "$unmute ", "$clear ", "$custom "]

client = discord.Client()
dynamo.init()


@client.event
async def on_message(message):
    if message.author.id in coned:
        await message.add_reaction("\U0001F4A9")
        await message.add_reaction("\U0001F1F8")
        await message.add_reaction("\U0001F1ED")
        await message.add_reaction("\U0001F1E6")
        await message.add_reaction("\U0001F1F2")
        await message.add_reaction("\U0001F1EA")

    if not has_power(message):
        await message.channel.send("YOU DON'T GOT THE POWER!")
        return

    if message.content.startswith('$uncone '):
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
    if message.content.startswith('$cone '):
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
    if message.content.startswith('$who'):
        msg = ""
        for user in coned:
            msg = msg + coned.get(user, "") + " "
        if msg != "":
            await message.channel.send(msg)
        else:
            await message.channel.send("Currently none")
        return

    if message.content.startswith('$mute '):
        mentions = message.mentions
        for user in mentions:
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            await message.channel.set_permissions(user, overwrite=overwrite)
            await message.channel.send(user.mention + " has been silenced")
        return

    if message.content.startswith('$unmute '):
        mentions = message.mentions
        for user in mentions:
            await message.channel.set_permissions(user, overwrite=None)
            await message.channel.send(user.mention + " has been forgiven")
        return

    if message.content.startswith('$clear '):
        try:
            parsed = message.content.split()
            global deleteMessage
            deleteMessage = message
            deleted = await message.channel.purge(limit=int(parsed[1]), check=is_person)
            await message.channel.send('Deleted {} message(s)'.format(len(deleted)))
        except Exception as e:
            await message.channel.send("Invalid Command")
        return

    if message.content.startswith('$custom '):
        try:
            parsed = message.content.split()
            if len(parsed) < 2:
                raise Exception()
            command = parsed[1]
            value = ""
            for part in parsed[2:]:
                value += part + " "
            if dynamo.add_custom_command(command, value) == "deleted":
                await message.channel.send("Command deleted!")
            else:
                await message.channel.send("Mission Accomplished")
        except Exception as e:
            print(e)
            await message.channel.send("Invalid Command")
        return

    if message.content.startswith('$'):
        response = dynamo.get_custom_command(message.content[1:])
        if response is not None:
            await message.channel.send(response)


def is_person(m):
    mentions = deleteMessage.mentions
    if len(mentions) == 0:
        return True
    return m.author == deleteMessage.mentions[0]


@client.event
async def on_member_join(member):
    msg = "Assalamualaikum " + member.mention + "! Welcome to **Muslim Gamers**! Please take a moment to introduce "
    msg += "yourself! You may only chat here for the time being until you reach lvl 1.\n\n"
    msg += "**You gain lvls by chatting!**\nAfter reaching lvl 1 you will gain access to the rest of the chats.\n\n"
    msg += "Feel free to read " + client.get_channel(rulesChat).mention + " and follow them accordingly.\n"
    msg += "Also check out " + client.get_channel(announcementsChat).mention
    msg += " for the latest things happening in the server.\n"
    await client.get_channel(welcomeChat).send(msg)


@client.event
async def on_member_remove(member):
    msg = member.mention + " just left **Muslim Gamers**. Bye bye " + member.mention + "..."
    await client.get_channel(welcomeChat).send(msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def has_power(message):
    for command in modCommands:
        if message.content.startswith(
                command) and message.author.top_role.id != 365541261156941829 and message.author.top_role.id != 287369489987928075 and message.author.top_role.id != 192322577207787523 and message.author.top_role.id != 193105896010809344:
            return False
    return True


client.run(TOKEN)
