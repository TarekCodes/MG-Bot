from cache import add_welcome_message, get_welcome_message_id
from discord.ext import commands
from textwrap import dedent
import discord
import datetime

from discord.message import Message

voice_role_id = 684253062143016971
afk_channel_id = 513411791116828692
bot_log = 245252349587619840
roles_chat_id = 365624761398591489
rules_chat_id = 458786996022673408
announcements_chat_id = 349679027126272011
welcome_chat_id = 334014732572950528
botspam_channel_id = 463874995169394698
game_night_club_role_id = 701876858009944066
color_url_prefix = "https://www.color-hex.com/color/"
level_one_role_id = 373141121502674946

class EventLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        role = guild.get_role(voice_role_id)
        if after.channel is not None and after.channel.id != afk_channel_id:
            await member.add_roles(role, atomic=True)
        else:
            await member.remove_roles(role, atomic=True)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        await self.check_role_change(before, after)
        await self.check_nickname_change(before, after)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        msg = dedent("""
        Salaams {user}! Welcome to **Muslim Gamers**!

        Please take some time to introduce yourself here. 
        **You'll unlock the rest of the server once you posted enough here to reach level 1.**

        **If you have issues with phone verification, please reach out to the Community Mods.**""").format(
            user=member.mention)
        # Send the welcome message and save it in the cache
        message: Message = await self.bot.get_channel(welcome_chat_id).send(msg)
        add_welcome_message(member.id, message.id)

        await self.member_join_log(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # msg = member.name + " just left **Muslim Gamers**. Bye bye " + member.mention + "..."
        # await self.bot.get_channel(botspam_channel_id).send(msg)

        # If the user has recently joined the server,
        #  delete their welcome message
        message_id: int = get_welcome_message_id(member.id)
        if (message_id != None):
            channel = self.bot.get_channel(welcome_chat_id)
            message: Message = await channel.fetch_message(message_id)
            await message.delete()

        await self.member_leave_log(member)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(
            description=user.mention + " {}#{}".format(user.name, user.discriminator),
            timestamp=datetime.datetime.utcnow(), color=discord.Color.red())
        embed.set_author(name="Member Banned", icon_url=user.avatar_url)
        embed.set_footer(text="ID: " + str(user.id))
        embed.set_thumbnail(url=user.avatar_url)
        await self.bot.get_channel(bot_log).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(
            description=user.mention + " {}#{}".format(user.name, user.discriminator),
            timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        embed.set_author(name="Member Unbanned", icon_url=user.avatar_url)
        embed.set_footer(text="ID: " + str(user.id))
        embed.set_thumbnail(url=user.avatar_url)
        await self.bot.get_channel(bot_log).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        embed = discord.Embed(
            description="**Channel Created: #{}**".format(channel.name),
            timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
        embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon_url)
        embed.set_footer(text="ID: " + str(channel.id))
        await self.bot.get_channel(bot_log).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        embed = discord.Embed(
            description="**Channel Deleted: #{}**".format(channel.name),
            timestamp=datetime.datetime.utcnow(), color=discord.Color.red())
        embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon_url)
        embed.set_footer(text="ID: " + str(channel.id))
        await self.bot.get_channel(bot_log).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        embed = discord.Embed(description=":crossed_swords:** Role Created: {}**".format(role.name),
                              timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
        embed.set_footer(text="ID: " + str(role.id))
        embed.add_field(name="Permissions",
                        value=self.get_perms(list(filter(self.filter_perms, iter(role.permissions)))))
        await self.bot.get_channel(bot_log).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        embed = discord.Embed(description=":wastebasket: ** Role Deleted: {}**".format(role.name),
                              timestamp=datetime.datetime.utcnow(), color=discord.Color.red())
        embed.set_footer(text="ID: " + str(role.id))
        embed.add_field(name="Color",
                        value="[{}]({}{})".format(str(role.color), color_url_prefix, str(role.color).replace("#", "")),
                        inline=False)
        embed.add_field(name="Permissions",
                        value=self.get_perms(list(filter(self.filter_perms, iter(role.permissions)))))
        await self.bot.get_channel(bot_log).send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print('------')

    async def check_role_change(self, before, after):
        if len(before.roles) == len(after.roles):
            return
        embed = None
        if len(before.roles) > len(after.roles):
            for role in before.roles:
                if role not in after.roles and role.id != voice_role_id:
                    embed = discord.Embed(
                        description=after.mention + " **was removed from the** `" + role.name + "` **role**",
                        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        else:
            for role in after.roles:
                if role not in before.roles and role.id != voice_role_id:
                    embed = discord.Embed(description=after.mention + " **was given the** `" + role.name + "` **role**",
                                          timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
                if role.id == level_one_role_id:
                    game_night_role = discord.utils.get(after.guild.roles, id=game_night_club_role_id)
                    await after.add_roles(game_night_role, atomic=True)
        try:
            embed.set_author(name=after.display_name, icon_url=after.avatar_url)
            embed.set_footer(text="ID: " + str(after.id))
            await self.bot.get_channel(bot_log).send(embed=embed)
        except Exception as e:
            return

    async def check_nickname_change(self, before, after):
        try:
            if before.nick == after.nick:
                return
        except Exception as e:
            return
        embed = discord.Embed(
            description=after.mention + " **Nickname Changed**",
            timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        embed.set_author(name="{}#{}".format(after.name, after.discriminator), icon_url=after.avatar_url)
        embed.set_footer(text="ID: " + str(after.id))
        embed.add_field(name="Before",
                        value=before.nick,
                        inline=False)
        embed.add_field(name="After",
                        value=after.nick,
                        inline=False)
        await self.bot.get_channel(bot_log).send(embed=embed)

    async def member_join_log(self, member):
        embed = discord.Embed(
            description=member.mention + " {}#{}".format(member.name, member.discriminator),
            timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
        embed.set_author(name="Member Joined", icon_url=member.avatar_url)
        embed.set_footer(text="ID: " + str(member.id))
        embed.set_thumbnail(url=member.avatar_url)
        await self.bot.get_channel(bot_log).send(embed=embed)

    async def member_leave_log(self, member):
        embed = discord.Embed(
            description=member.mention + " {}#{}".format(member.name, member.discriminator),
            timestamp=datetime.datetime.utcnow(), color=discord.Color.red())
        embed.set_author(name="Member Left", icon_url=member.avatar_url)
        embed.set_footer(text="ID: " + str(member.id))
        embed.set_thumbnail(url=member.avatar_url)
        await self.bot.get_channel(bot_log).send(embed=embed)

    @staticmethod
    def filter_perms(perm):
        return perm[1]

    @staticmethod
    def get_perms(perms):
        perms_list = ""
        for perm in perms:
            if perms_list != "":
                perms_list += ", "
            perms_list += (perm[0])
        perms_list = perms_list.replace("_", " ")
        return perms_list


def setup(bot):
    bot.add_cog(EventLogging(bot))
