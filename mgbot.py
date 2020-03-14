import config
import dynamo
import moderation
import miscellaneous as misc
from discord.ext import commands

TOKEN = config.botToken
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

initial_extensions = ['cogs.moderation', 'cogs.misc', 'cogs.suggestions', 'cogs.eventlogging', 'cogs.reddit',
                      'cogs.autoroles']

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
