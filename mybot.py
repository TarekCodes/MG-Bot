import discord
import config
import dynamo

TOKEN = config.botToken
coned = {}
welcomeChat = '334014732572950528'
announcementsChat = '349679027126272011'
rulesChat = '365624761398591489'
deleteMessage = None
modCommands = ["$uncone ", "$cone ", "$who", "$mute ", "$unmute ", "$clear ", "$custom "]

client = discord.Client()
dynamo.init()


@client.event
async def on_message(message):
    if message.author.id in coned:
        await client.add_reaction(message, "\U0001F4A9")
        await client.add_reaction(message, "\U0001F1F8")
        await client.add_reaction(message, "\U0001F1ED")
        await client.add_reaction(message, "\U0001F1E6")
        await client.add_reaction(message, "\U0001F1F2")
        await client.add_reaction(message, "\U0001F1EA")

    if not has_power(message):
        await client.send_message(message.channel, "YOU DON'T GOT THE POWER!")
        return

    if message.content.startswith('$uncone '):
        mentions = message.mentions
        for user in mentions:
            if user.id in coned:
                try:
                    await client.change_nickname(user, coned.get(user.id, None))
                except discord.Forbidden:
                    print("Can't change nickname")
                del coned[user.id]
                await client.send_message(message.channel, user.mention + " unconed")
            else:
                await client.send_message(message.channel, user.mention + " wasn't coned")
        return
    if message.content.startswith('$cone '):
        mentions = message.mentions
        for user in mentions:
            coned[user.id] = user.nick
            try:
                await client.change_nickname(user, "CONE OF SHAME!")
            except discord.Forbidden:
                print("Can't change nickname")
            await client.send_message(message.channel, "Shame on you! " + user.mention)
        return
    if message.content.startswith('$who'):
        msg = ""
        for user in coned:
            msg = msg + coned.get(user, "") + " "
        if msg != "":
            await client.send_message(message.channel, msg)
        else:
            await client.send_message(message.channel, "Currently none")
        return

    if message.content.startswith('$mute '):
        mentions = message.mentions
        for user in mentions:
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            await client.edit_channel_permissions(message.channel, user, overwrite)
            await client.send_message(message.channel, user.mention + " has been silenced")
        return

    if message.content.startswith('$unmute '):
        mentions = message.mentions
        for user in mentions:
            await client.delete_channel_permissions(message.channel, user)
            await client.send_message(message.channel, user.mention + " has been forgiven")
        return

    if message.content.startswith('$clear '):
        try:
            parsed = message.content.split()
            global deleteMessage
            deleteMessage = message
            deleted = await client.purge_from(message.channel, limit=int(parsed[1]), check=is_person)
            await client.send_message(message.channel, 'Deleted {} message(s)'.format(len(deleted)))
        except Exception as e:
            await client.send_message(message.channel, "Invalid Command")
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
                await client.send_message(message.channel, "Command deleted!")
            else:
                await client.send_message(message.channel, "Mission Accomplished")
        except Exception as e:
            print(e)
            await client.send_message(message.channel, "Invalid Command")
        return

    if message.content.startswith('$'):
        response = dynamo.get_custom_command(message.content[1:])
        if response is not None:
            await client.send_message(message.channel, response)


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
    await client.send_message(client.get_channel(welcomeChat), msg)


@client.event
async def on_member_remove(member):
    msg = member.mention + " just left **Muslim Gamers**. Bye bye " + member.mention + "..."
    await client.send_message(client.get_channel(welcomeChat), msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def has_power(message):
    for command in modCommands:
        if message.content.startswith(
                command) and message.author.top_role.id != '365541261156941829' and message.author.top_role.id != '287369489987928075' and message.author.top_role.id != '192322577207787523' and message.author.top_role.id != '193105896010809344':
            return False
    return True


client.run(TOKEN)
