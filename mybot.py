import config
import dynamo
import discord
import moderation
import miscellaneous as misc

TOKEN = config.botToken
roleEmojis = {}
customRoleEmojis = {}
roles_msgs = []
welcomeChat = 334014732572950528
announcementsChat = 349679027126272011
suggestions_chat = 480459932164947969
roles_chat = 365624761398591489
rules_chat = 458786996022673408
bot_log = 245252349587619840

modCommands = ["$uncone ", "$cone ", "$coned", "$mute ", "$unmute ", "$clear ", "$custom ", "$servermute ",
               "$serverunmute ", "$help", "$mutechannel", "$unmutechannel", "$suggestions "]

client = discord.Client()
dynamo.init()


@client.event
async def on_message(message):
    if message.guild is None and message.content.startswith('suggestion: '):
        await misc.new_suggestion(message, client, suggestions_chat)
        return

    if moderation.is_coned(message.author.id):
        await moderation.cone_message(message)

    if not has_power(message):
        await message.channel.send("YOU DON'T GOT THE POWER!")
        return

    if message.content.startswith('$uncone '):
        await moderation.uncone(message)
        return
    if message.content.startswith('$cone '):
        await moderation.cone(message)
        return
    if message.content.startswith('$coned'):
        await moderation.get_coned(message)
        return
    if message.content.startswith('$mute '):
        await moderation.mute(message)
        return
    if message.content.startswith('$unmute '):
        await moderation.unmute(message)
        return
    if message.content.startswith('$servermute '):
        await moderation.server_mute(message)
        return
    if message.content.startswith('$serverunmute '):
        await moderation.server_unmute(message)
        return
    if message.content.startswith('$clear '):
        await moderation.clear(message)
        return
    if message.content.startswith('$invitelink'):
        await misc.invite_link(message)
        return
    if message.content.startswith('$custom '):
        await misc.custom(message)
        return
    if message.content.startswith('$'):
        response = dynamo.get_custom_command(message.content[1:])
        if response is not None:
            await message.channel.send(response)
    if message.content == '$help':
        await misc.help(message)
        return
    if message.content == '$mutechannel':
        await moderation.mute_channel(message)
        return
    if message.content == '$unmutechannel':
        await moderation.unmute_channel(message)
        return
    if message.content.startswith('$suggestions '):
        await misc.get_suggestions(message, client, bot_log)
        return


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


# @client.event
# async def on_member_remove(member):
#     msg = member.name + " just left **Muslim Gamers**. Bye bye " + member.mention + "..."
#     await client.get_channel(welcomeChat).send(msg)


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
    rules_channel = client.get_channel(roles_chat)
    for emoji in roleEmojis:
        for current_msg in roles_msgs:
            msg = await rules_channel.get_message(current_msg)
            try:
                if emoji in customRoleEmojis:
                    await msg.add_reaction(client.get_emoji(customRoleEmojis.get(emoji)))
                else:
                    await msg.add_reaction(emoji)
                break
            except Exception as e:
                print('next msg')


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
    roleEmojis["🤺"] = "For Honor"
    roleEmojis["🎣"] = "World of Warcraft"
    roleEmojis["🎇"] = "StarCraft"
    roleEmojis["🕋"] = "Team Quran"
    roleEmojis["🤖"] = "TennoFrame"
    roleEmojis["🐊"] = "Monster Hunters"
    roleEmojis["🔄"] = "Nintendo Switch"
    roleEmojis["🤠"] = "The Steves"
    roleEmojis["⛓"] = "Sirat-ul-Exile"
    roleEmojis["🔰"] = "Keyboard Warriors"
    roleEmojis["🐸"] = "Fascist Scum"

    customRoleEmojis["chickenleg"] = 319229845957640192
    customRoleEmojis["runescape"] = 455087244898992129

    roles_msgs.append(398539277035896846)
    roles_msgs.append(458465086693048341)
    roles_msgs.append(460218391781965824)


def has_power(message):
    for command in modCommands:
        if message.content.startswith(
                command) and message.author.top_role.id != 365541261156941829 and message.author.top_role.id != 287369489987928075 and message.author.top_role.id != 192322577207787523 and message.author.top_role.id != 193105896010809344:
            return False
    return True


client.run(TOKEN)
