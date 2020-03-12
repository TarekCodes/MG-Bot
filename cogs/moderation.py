import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coned = {}

    @commands.command()
    async def uncone(self, ctx, members: commands.Greedy[discord.Member]):
        for member in members:
            if member.id in self.coned:
                try:
                    await member.edit(nick=self.coned.get(member.id, None))
                except discord.Forbidden:
                    print("Can't change nickname")
                del self.coned[member.id]
                await ctx.channel.send(member.mention + " unconed")
            else:
                await ctx.channel.send(member.mention + " wasn't coned")
        return

    @commands.command()
    async def cone(self, ctx, members: commands.Greedy[discord.Member]):
        for member in members:
            if member.nick is None:
                self.coned[member.id] = member.name
            else:
                self.coned[member.id] = member.nick
            try:
                await member.edit(nick="CONE OF SHAME!")
            except discord.Forbidden:
                print("Can't change nickname")
            await ctx.send("Shame on you! " + member.mention)
        return

    @commands.command(name="coned")
    async def get_coned(self, message):
        msg = ""
        for member in self.coned:
            msg = msg + self.coned.get(member, "") + " "
        if msg != "":
            await message.channel.send(msg)
        else:
            await message.channel.send("Currently none")
        return

    @commands.command()
    async def mute(self, ctx, members: commands.Greedy[discord.Member]):
        for member in members:
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            await ctx.channel.set_permissions(member, overwrite=overwrite)
            await ctx.channel.send(member.mention + " has been silenced")
        return

    @commands.command()
    async def unmute(self, ctx, members: commands.Greedy[discord.Member]):
        for member in members:
            await ctx.channel.set_permissions(member, overwrite=None)
            await ctx.channel.send(member.mention + " has been forgiven")
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.is_coned(message.author.id):
            await self.cone_message(message)

    def is_coned(self, member_id):
        return member_id in self.coned

    async def cone_message(self, message):
        await message.add_reaction("\U0001F4A9")
        await message.add_reaction("\U0001F1F8")
        await message.add_reaction("\U0001F1ED")
        await message.add_reaction("\U0001F1E6")
        await message.add_reaction("\U0001F1F2")
        await message.add_reaction("\U0001F1EA")


def setup(bot):
    bot.add_cog(Moderation(bot))
