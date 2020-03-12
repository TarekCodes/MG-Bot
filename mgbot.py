import config
import dynamo
import discord
import moderation
import miscellaneous as misc
import reddit
import eventlogging
from discord.ext import commands

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
bot_spam = 463874995169394698
team_leads_role = 676618335059968001
president_role = 192322577207787523
advisory_role = 287369489987928075
events_lead_role = 674291368088305664
mods_role = 365541261156941829
admin_role = 193105896010809344
infra_team_role = 674287256499912710
infra_lead_role = 674291078760759317
afk_channel_id = 513411791116828692
voice_role_id = 684253062143016971

modCommands = ["$uncone ", "$cone ", "$coned", "$mute ", "$unmute ", "$clear ", "$custom ", "$servermute ",
               "$serverunmute ", "$help", "$mutechannel", "$unmutechannel", "$suggestions ", "$suggestion ", "$reddit ",
               "$getallcustom", "$phrase ", "$question"]

initial_extensions = ['cogs.moderation', 'cogs.misc']

bot = commands.Bot(command_prefix='$', case_insensitive=False, description="MG Bot")
for extension in initial_extensions:
    bot.load_extension(extension)
dynamo.init()


# @bot.event
async def on_message(message):
    if message.guild is None and message.content.lower().startswith('suggestion: '):
        await misc.new_suggestion(message, bot, suggestions_chat)
        return

    if not has_power(message):
        await message.channel.send("YOU DON'T GOT THE POWER!")
        return

    if message.content.startswith('$question'):
        await misc.get_question(message)
        return
    if message.content.startswith('$answer '):
        await misc.answer_question(message)
        return
    if message.content.startswith('$score'):
        await misc.get_score(message)
        return
    if message.content.startswith('$fightme '):
        await misc.fight(message)
        return
    if message.content.startswith('$phrase '):
        await misc.new_phrase(message)
        return
    if message.content.startswith('$bansuggestions '):
        await misc.ban_suggestions(message)
        return
    if message.content.startswith('$unbansuggestions '):
        await misc.unban_suggestions(message)
        return
    if message.content == "$getallcustom":
        response = dynamo.get_all_custom()
        for msg in response:
            await message.channel.send(msg)
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
        await misc.get_suggestions(message, bot, bot_log)
        return
    if message.content.startswith('$suggestion '):
        await misc.get_suggestion(message, bot, bot_log)
        return
    if message.content.startswith('$reddit '):
        await reddit.get_top_post(message)
        return
    if message.content.startswith('$startgiveaway '):
        await misc.start_giveaway(message)
        return
    if message.content.startswith('$endgiveaway '):
        await misc.end_giveaway(bot, message)
        return
    # handle phrase
    val = dynamo.get_phrase(message.content)
    if val is not None and message.author.id != bot.user.id:
        await message.channel.send(val)
        return


@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    role = guild.get_role(voice_role_id)
    if after.channel is not None and after.channel.id != afk_channel_id:
        await member.add_roles(role, atomic=True)
    else:
        await member.remove_roles(role, atomic=True)


@bot.event
async def on_member_update(before, after):
    await eventlogging.check_role_change(before, after, bot)
    await eventlogging.check_nickname_change(before, after, bot)


@bot.event
async def on_member_join(member):
    msg = "Assalamualaikum " + member.mention + "! Welcome to **Muslim Gamers**! Please take a moment to introduce "
    msg += "yourself! You may only chat here for the time being until you reach lvl 1.\n\n"
    msg += "**You gain lvls by chatting!** After reaching lvl 1 you will gain access to the rest of the chats.\n\n"
    msg += "**Checkout the roles we have over at " + bot.get_channel(roles_chat).mention + " and react "
    msg += "to the messages to give yourself the ones you like.**\n\n"
    msg += "Feel free to read " + bot.get_channel(rules_chat).mention + " and follow them accordingly.\n"
    msg += "Also check out " + bot.get_channel(announcementsChat).mention
    msg += " for the latest things happening in the server.\n"
    await bot.get_channel(welcomeChat).send(msg)
    await eventlogging.member_join_log(member, bot)


@bot.event
async def on_member_remove(member):
    msg = member.name + " just left **Muslim Gamers**. Bye bye " + member.mention + "..."
    await bot.get_channel(bot_spam).send(msg)
    await eventlogging.member_leave_log(member, bot)


@bot.event
async def on_member_ban(guild, user):
    await eventlogging.member_ban_log(user, bot)


@bot.event
async def on_member_unban(guild, user):
    await eventlogging.member_unban_log(user, bot)


@bot.event
async def on_guild_channel_create(channel):
    await eventlogging.channel_create_log(channel, bot)


@bot.event
async def on_guild_channel_delete(channel):
    await eventlogging.channel_delete_log(channel, bot)


@bot.event
async def on_guild_role_create(role):
    await eventlogging.role_create_log(role, bot)


@bot.event
async def on_guild_role_delete(role):
    await eventlogging.role_delete_log(role, bot)


@bot.event
async def on_raw_reaction_add(payload):
    # handle giveaways
    if dynamo.get_giveaway(
            payload.message_id) is not None and payload.emoji.name == "🏆" and payload.user_id != 447970747076575232:
        if dynamo.new_giveaway_entry(payload.user_id, payload.message_id):
            await bot.get_channel(payload.channel_id).guild.get_member(payload.user_id).send(
                "You have been entered in the giveaway. Good luck!")
    if payload.message_id in roles_msgs:
        guild = bot.get_channel(payload.channel_id).guild
        user = guild.get_member(payload.user_id)
        role_name = roleEmojis.get(payload.emoji.name, None)
        if role_name is not None:
            role = discord.utils.get(guild.roles, name=role_name)
            await user.add_roles(role, atomic=True)


@bot.event
async def on_raw_reaction_remove(payload):
    # handle giveaways
    if dynamo.get_giveaway(payload.message_id) is not None and payload.emoji.name == "🏆":
        dynamo.delete_giveaway_entry(payload.user_id, payload.message_id)
        await bot.get_channel(payload.channel_id).guild.get_member(payload.user_id).send(
            "Your entry has been removed.")
    if payload.message_id in roles_msgs:
        guild = bot.get_channel(payload.channel_id).guild
        user = guild.get_member(payload.user_id)
        role_name = roleEmojis.get(payload.emoji.name, None)
        if role_name is not None:
            role = discord.utils.get(guild.roles, name=role_name)
            try:
                await user.remove_roles(role, atomic=True)
            except Exception as e:
                print("couldn't remove role")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    setup_emojis()
    # await set_up_roles_msg()


async def set_up_roles_msg():
    rules_channel = bot.get_channel(roles_chat)
    for emoji in roleEmojis:
        for current_msg in roles_msgs:
            msg = await rules_channel.fetch_message(current_msg)
            try:
                if emoji in customRoleEmojis:
                    await msg.add_reaction(bot.get_emoji(customRoleEmojis.get(emoji)))
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
    roleEmojis["🕋"] = "Lecture"
    roleEmojis["🤖"] = "TennoFrame"
    roleEmojis["🐊"] = "Monster Hunters"
    roleEmojis["🔄"] = "Nintendo Switch"
    roleEmojis["🤠"] = "The Steves"
    roleEmojis["⛓"] = "Sirat-ul-Exile"
    roleEmojis["🔰"] = "Keyboard Warriors"
    roleEmojis["🐸"] = "Fascist Scum"
    roleEmojis["🏳"] = "Farm Simulator"
    roleEmojis["👊🏾"] = "Button Mashers"
    roleEmojis["🎮"] = "Apex Legends"
    roleEmojis["🇱"] = "League of Losers EU"
    roleEmojis["⚔"] = "Hodor"
    roleEmojis["👷🏾"] = "Rainbow Six Siege"
    roleEmojis["😇"] = "Halo"
    roleEmojis["🌠"] = "Stormtrooper"
    roleEmojis["💳"] = "Tarnoobz"
    roleEmojis["⚠"] = "Going Dark"
    roleEmojis["🍿"] = "Coke and Popcorn"

    customRoleEmojis["chickenleg"] = 319229845957640192
    customRoleEmojis["runescape"] = 455087244898992129

    roles_msgs.append(398539277035896846)
    roles_msgs.append(458465086693048341)
    roles_msgs.append(460218391781965824)
    roles_msgs.append(633304992719306762)


def has_power(message):
    for command in modCommands:
        if message.content.startswith(
                command) and message.author.top_role.id != president_role and \
                message.author.top_role.id != team_leads_role and \
                message.author.top_role.id != events_lead_role and message.author.top_role.id != mods_role and \
                message.author.top_role.id != admin_role and message.author.top_role.id != infra_lead_role:
            return False
    return True


bot.run(TOKEN)
