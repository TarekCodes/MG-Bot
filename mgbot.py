import config
import dynamo
import discord
import moderation
import miscellaneous as misc
import reddit
from discord.ext import commands

TOKEN = config.botToken
roleEmojis = {}
customRoleEmojis = {}
roles_msgs = []
roles_chat = 365624761398591489
bot_log = 245252349587619840
team_leads_role = 676618335059968001
president_role = 192322577207787523
advisory_role = 287369489987928075
events_lead_role = 674291368088305664
mods_role = 365541261156941829
admin_role = 193105896010809344
infra_team_role = 674287256499912710
infra_lead_role = 674291078760759317

modCommands = ["$uncone ", "$cone ", "$coned", "$mute ", "$unmute ", "$clear ", "$custom ", "$servermute ",
               "$serverunmute ", "$help", "$mutechannel", "$unmutechannel", "$suggestions ", "$suggestion ", "$reddit ",
               "$getallcustom", "$phrase ", "$question"]

initial_extensions = ['cogs.moderation', 'cogs.misc', 'cogs.suggestions', 'cogs.eventlogging']

bot = commands.Bot(command_prefix='$', case_insensitive=False, description="MG Bot")
for extension in initial_extensions:
    bot.load_extension(extension)
dynamo.init()


# @bot.event
async def on_message(message):
    if not has_power(message):
        await message.channel.send("YOU DON'T GOT THE POWER!")
        return
    if message.content == '$help':
        await misc.help(message)
        return
    if message.content == '$mutechannel':
        await moderation.mute_channel(message)
        return
    if message.content == '$unmutechannel':
        await moderation.unmute_channel(message)
        return
    if message.content.startswith('$reddit '):
        await reddit.get_top_post(message)
        return


@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id in roles_msgs:
        guild = bot.get_channel(payload.channel_id).guild
        user = guild.get_member(payload.user_id)
        role_name = roleEmojis.get(payload.emoji.name, None)
        if role_name is not None:
            role = discord.utils.get(guild.roles, name=role_name)
            await user.add_roles(role, atomic=True)


@bot.event
async def on_raw_reaction_remove(payload):
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
