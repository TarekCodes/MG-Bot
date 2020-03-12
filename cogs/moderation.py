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

    @commands.command(name="coned")
    async def get_coned(self, message):
        msg = ""
        for member in self.coned:
            msg = msg + self.coned.get(member, "") + " "
        if msg != "":
            await message.channel.send(msg)
        else:
            await message.channel.send("Currently none")

    @commands.command()
    async def mute(self, ctx, members: commands.Greedy[discord.Member]):
        for member in members:
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            await ctx.channel.set_permissions(member, overwrite=overwrite)
            await ctx.channel.send(member.mention + " has been silenced")

    @commands.command()
    async def unmute(self, ctx, members: commands.Greedy[discord.Member]):
        for member in members:
            await ctx.channel.set_permissions(member, overwrite=None)
            await ctx.channel.send(member.mention + " has been forgiven")

    @commands.command(name="servermute")
    async def server_mute(self, ctx, members: commands.Greedy[discord.Member]):
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.speak = False
        channels = ctx.guild.channels
        for member in members:
            for channel in channels:
                try:
                    await channel.set_permissions(member, overwrite=overwrite)
                except Exception as e:
                    print(e)
            await ctx.channel.send("You're annoying " + member.mention)

    @commands.command(name="serverunmute")
    async def server_unmute(self, ctx, members: commands.Greedy[discord.Member]):
        channels = ctx.guild.channels
        for member in members:
            for channel in channels:
                try:
                    await channel.set_permissions(member, overwrite=None)
                except Exception as e:
                    print(e)
            await ctx.channel.send("Better not do it again " + member.mention)

    @commands.command()
    async def clear(self, ctx, num: int, *members: commands.Greedy[discord.Member]):
        check = (lambda m: m.author in members) if members else None
        deleted = await ctx.channel.purge(limit=num + 1, check=check)
        await ctx.channel.send('Deleted {} message(s)'.format(len(deleted)))

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
