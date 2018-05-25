import discord
import config

TOKEN = config.botToken
coned = {}
welcomeChat = '334014732572950528'
announcementsChat = '349679027126272011'
rulesChat = '365624761398591489'

client = discord.Client()


@client.event
async def on_message(message):
    if message.content.startswith(
            '$') and message.author.top_role.id != '365541261156941829' and message.author.top_role.id != '287369489987928075' and message.author.top_role.id != '192322577207787523' and message.author.top_role.id != '193105896010809344':
        await client.send_message(message.channel, "YOU DON'T GOT THE POWER!")
        return

    if message.author.id in coned:
        await client.add_reaction(message, "\U0001F4A9")
        await client.add_reaction(message, "\U0001F1F8")
        await client.add_reaction(message, "\U0001F1ED")
        await client.add_reaction(message, "\U0001F1E6")
        await client.add_reaction(message, "\U0001F1F2")
        await client.add_reaction(message, "\U0001F1EA")
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
    if message.content.startswith('$cone '):
        mentions = message.mentions
        for user in mentions:
            coned[user.id] = user.nick
            try:
                await client.change_nickname(user, "CONE OF SHAME!")
            except discord.Forbidden:
                print("Can't change nickname")
            await client.send_message(message.channel, "Shame on you! " + user.mention)
    if message.content.startswith('$who'):
        msg = ""
        for user in coned:
            msg = msg + coned.get(user, "") + " "
        if msg != "":
            await client.send_message(message.channel, msg)
        else:
            await client.send_message(message.channel, "Currently none")

    if message.content.startswith('$mute '):
        mentions = message.mentions
        for user in mentions:
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            await client.edit_channel_permissions(message.channel, user, overwrite)
            await client.send_message(message.channel, user.mention + " has been silenced")

    if message.content.startswith('$unmute '):
        mentions = message.mentions
        for user in mentions:
            await client.delete_channel_permissions(message.channel, user)
            await client.send_message(message.channel, user.mention + " has been forgiven")


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


client.run(TOKEN)
