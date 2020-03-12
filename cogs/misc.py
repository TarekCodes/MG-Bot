import discord
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
