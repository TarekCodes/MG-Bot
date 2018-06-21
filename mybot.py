import config
import dynamo
import discord

TOKEN = config.botToken
coned = {}
roleEmojis = {}
customRoleEmojis = {}
roles_msgs = []
welcomeChat = 334014732572950528
announcementsChat = 349679027126272011
roles_chat = 365624761398591489
rules_chat = 458786996022673408
deleteMessage = None
modCommands = ["$uncone ", "$cone ", "$coned", "$mute ", "$unmute ", "$clear ", "$custom "]

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
    if message.content.startswith('$coned'):
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

    if message.content.startswith('$invitelink'):
        await message.channel.send("https://discord.gg/ErTb8t3")
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
    msg += "**You gain lvls by chatting!** After reaching lvl 1 you will gain access to the rest of the chats.\n\n"
    msg += "**Checkout the roles we have over at " + client.get_channel(roles_chat).mention + " and react "
    msg += "to the messages to give yourself the ones you like.**\n\n"
    msg += "Feel free to read " + client.get_channel(rules_chat).mention + " and follow them accordingly.\n"
    msg += "Also check out " + client.get_channel(announcementsChat).mention
    msg += " for the latest things happening in the server.\n"
    await client.get_channel(welcomeChat).send(msg)


@client.event
async def on_member_remove(member):
    msg = member.mention + " just left **Muslim Gamers**. Bye bye " + member.mention + "..."
    await client.get_channel(welcomeChat).send(msg)


@client.event
async def on_raw_reaction_add(emoji, msg_id, channel_id, user_id):
    if msg_id in roles_msgs:
        guild = client.get_channel(channel_id).guild
        user = guild.get_member(user_id)
        role_name = roleEmojis.get(emoji.name, None)
        if role_name is not None:
            role = discord.utils.get(guild.roles, name=role_name)
            await user.add_roles(role, atomic=True)


@client.event
async def on_raw_reaction_remove(emoji, msg_id, channel_id, user_id):
    if msg_id in roles_msgs:
        guild = client.get_channel(channel_id).guild
        user = guild.get_member(user_id)
        role_name = roleEmojis.get(emoji.name, None)
        if role_name is not None:
            role = discord.utils.get(guild.roles, name=role_name)
            try:
                await user.remove_roles(role, atomic=True)
            except Exception as e:
                print("couldn't remove role")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    setup_emojis()
    # await set_up_roles_msg()


async def set_up_roles_msg():
    count = 0
    current_msg = 0
    rules_channel = client.get_channel(roles_chat)
    msg = await rules_channel.get_message(roles_msgs[current_msg])
    for emoji in roleEmojis:
        if count >= 18:
            current_msg += 1
            msg = await rules_channel.get_message(roles_msgs[current_msg])
        if emoji in customRoleEmojis:
            await msg.remove_reaction(client.get_emoji(customRoleEmojis.get(emoji)), client.user)
            await msg.add_reaction(client.get_emoji(customRoleEmojis.get(emoji)))
        else:
            await msg.remove_reaction(emoji, client.user)
            await msg.add_reaction(emoji)
        count += 1


def setup_emojis():
    roleEmojis["🃏"] = "Road Blockers"
    roleEmojis["chickenleg"] = "PUBG Crew"
    roleEmojis["🐉"] = "League of Losers"
    roleEmojis["🏹"] = "Hanzo Mains"
    roleEmojis["🔫"] = "Rush B Watch Cat"
    roleEmojis["💀"] = "Dead by Daylight"
    roleEmojis["⚛"] = "Ancient Defenders"
    roleEmojis["⚽"] = "Learning to Dribble"
    roleEmojis["💠"] = "Guardians"
    roleEmojis["🛠"] = "Master Builders"
    roleEmojis["🐛"] = "Stick Fightin"
    roleEmojis["⛳"] = "Mini Golf Rules"
    roleEmojis["🌈"] = "Fuzing Hostage"
    roleEmojis["🎵"] = "music haramis"
    roleEmojis["runescape"] = "Osbuddies"
    roleEmojis["⚔"] = "Dauntless"
    roleEmojis["💸"] = "Cheap Gamers"
    roleEmojis["🗺"] = "Skribblio"
    roleEmojis["🔷"] = "Paladins"

    customRoleEmojis["chickenleg"] = 319229845957640192
    customRoleEmojis["runescape"] = 455087244898992129

    roles_msgs.append(398539277035896846)
    roles_msgs.append(458465086693048341)


def has_power(message):
    for command in modCommands:
        if message.content.startswith(
                command) and message.author.top_role.id != 365541261156941829 and message.author.top_role.id != 287369489987928075 and message.author.top_role.id != 192322577207787523 and message.author.top_role.id != 193105896010809344:
            return False
    return True


client.run(TOKEN)
