import discord
from discord.ext import commands

team_leads_role = 676618335059968001
president_role = 192322577207787523
events_lead_role = 674291368088305664
mods_role = 365541261156941829
admin_role = 193105896010809344
infra_team_role = 674287256499912710
infra_lead_role = 674291078760759317
socialmedia_lead_role = 674653557038776342
bots_role_id = 207996893769236481
muted_channels_overwrites = {}

allowed_roles = [team_leads_role, president_role, events_lead_role, mods_role, admin_role, infra_lead_role,
                 infra_team_role, socialmedia_lead_role, bots_role_id]

lead_roles = {team_leads_role, president_role, events_lead_role, admin_role, infra_lead_role}


def is_mod():
    async def predicate(ctx):
        return ctx.author.top_role.id in allowed_roles

    return commands.check(predicate)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coned = {}

    @is_mod()
    @commands.command(help="uncone users")
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

    @is_mod()
    @commands.command(help="cone users")
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

    @is_mod()
    @commands.command(name="coned", help="get all coned users")
    async def get_coned(self, message):
        msg = ""
        for member in self.coned:
            msg = msg + self.coned.get(member, "") + " "
        if msg != "":
            await message.channel.send(msg)
        else:
            await message.channel.send("Currently none")

    @is_mod()
    @commands.command(help="mute user in current channel")
    async def mute(self, ctx, members: commands.Greedy[discord.Member]):
        for member in members:
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            await ctx.channel.set_permissions(member, overwrite=overwrite)
            await ctx.channel.send(member.mention + " has been silenced")

    @is_mod()
    @commands.command(help="unmute user in current channel")
    async def unmute(self, ctx, members: commands.Greedy[discord.Member]):
        for member in members:
            await ctx.channel.set_permissions(member, overwrite=None)
            await ctx.channel.send(member.mention + " has been forgiven")

    @is_mod()
    @commands.command(name="servermute", help="server-wide mute")
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

    @is_mod()
    @commands.command(name="serverunmute", help="server-wide unmute")
    async def server_unmute(self, ctx, members: commands.Greedy[discord.Member]):
        channels = ctx.guild.channels
        for member in members:
            for channel in channels:
                try:
                    await channel.set_permissions(member, overwrite=None)
                except Exception as e:
                    print(e)
            await ctx.channel.send("Better not do it again " + member.mention)

    @is_mod()
    @commands.command(help="optionally specify a user to only target him/her")
    async def clear(self, ctx, num: int, *members: commands.Greedy[discord.Member]):
        check = (lambda m: m.author in members) if members else None
        deleted = await ctx.channel.purge(limit=num + 1, check=check)
        await ctx.channel.send('Deleted {} message(s)'.format(len(deleted)))

    @is_mod()
    @commands.command(name="mutechannel", help="mutes everyone except for mods")
    async def mute_channel(self, ctx):
        channel = ctx.channel
        overwrites = channel.overwrites
        muted_channels_overwrites[channel.name] = overwrites
        for role, overwrite in overwrites.items():
            if role.id not in allowed_roles and overwrite.send_messages is not False:
                cant_send = discord.PermissionOverwrite()
                cant_send.send_messages = False
                await channel.set_permissions(role, overwrite=cant_send)
        await ctx.channel.send("YOU SHALL NOT CHAT!")

    @is_mod()
    @commands.command(name="unmutechannel", help="brings the channel back to how it was")
    async def unmute_channel(self, ctx):
        channel = ctx.channel
        if channel.name not in muted_channels_overwrites:
            await channel.send("Channel wasn't muted")
            return
        overwrites = muted_channels_overwrites[channel.name]
        for role, overwrite in overwrites.items():
            await channel.set_permissions(role, overwrite=overwrite)
        del muted_channels_overwrites[channel.name]
        await channel.send("CHAT YOU FOOLS!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.is_coned(message.author.id):
            await self.cone_message(message)

    def is_coned(self, member_id):
        return member_id in self.coned

    @staticmethod
    async def cone_message(message):
        await message.add_reaction("\U0001F4A9")
        await message.add_reaction("\U0001F1F8")
        await message.add_reaction("\U0001F1ED")
        await message.add_reaction("\U0001F1E6")
        await message.add_reaction("\U0001F1F2")
        await message.add_reaction("\U0001F1EA")


def setup(bot):
    bot.add_cog(Moderation(bot))
