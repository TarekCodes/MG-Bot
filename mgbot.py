import config
import dynamo
from discord.ext import commands

TOKEN = config.botToken

initial_extensions = ['cogs.moderation', 'cogs.misc', 'cogs.suggestions', 'cogs.eventlogging', 'cogs.reddit',
                      'cogs.autoroles', 'cogs.trello']

bot = commands.Bot(command_prefix='$', case_insensitive=False, description="MG Bot")
for extension in initial_extensions:
    bot.load_extension(extension)
dynamo.init()

bot.run(TOKEN)
