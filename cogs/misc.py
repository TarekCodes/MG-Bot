import discord
import dynamo
from discord.ext import commands

welcome_chat_id = 334014732572950528


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coned = {}

    @commands.command(name="invitelink")
    async def invite_link(self, ctx):
        invite = await ctx.guild.get_channel(welcome_chat_id).create_invite(max_uses=1, max_age=1440,
                                                                            reason="created by " + str(ctx.author))
        await ctx.channel.send("New invite created for " + ctx.author.mention + " " + invite.url)

    @commands.command()
    async def custom(self, ctx, command, *value):
        try:
            value = " ".join(value)
            if dynamo.add_custom_command(command, value) == "deleted":
                await ctx.channel.send("Command deleted!")
            else:
                await ctx.channel.send("Mission Accomplished")
        except Exception as e:
            print(e)
            await ctx.channel.send("Invalid Command")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith('$'):
            response = dynamo.get_custom_command(message.content[1:])
            if response is not None:
                await message.channel.send(response)


def setup(bot):
    bot.add_cog(Misc(bot))
