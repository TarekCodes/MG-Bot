from discord.ext import commands
import discord
from .moderation import is_mod
import dynamo

roles_msgs = []
roles_chat_id = 365624761398591489


class AutoRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @is_mod()
    @commands.command(name="addroleemoji", help="adds a new role-emoji association")
    async def add_role_emoji(self, ctx, emoji, *role):
        role = " ".join(role)
        dynamo.add_role_emoji(emoji, role)
        embed = discord.Embed(color=discord.Color.green())
        embed.set_author(name="New emoji-role association", icon_url=ctx.guild.icon_url)
        embed.add_field(name="Emoji", value=emoji)
        embed.add_field(name="Role", value=role)
        await ctx.channel.send(embed=embed)
        await self.setup_emojis()

    @is_mod()
    @commands.command(name="deleteroleemoji", help="deletes a role-emoji association")
    async def delete_role_emoji(self, ctx, emoji):
        dynamo.delete_emoji_role(emoji)
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name="Deleted emoji-role association", icon_url=ctx.guild.icon_url)
        embed.add_field(name="Emoji", value=emoji)
        await ctx.channel.send(embed=embed)
        await self.setup_emojis()

    @is_mod()
    @commands.command(name="getallrolesemojis", help="gets all role-emoji associations")
    async def get_all_role_emoji(self, ctx):
        emojis_roles = dynamo.roles_cache
        embed = discord.Embed(color=discord.Color.blue())
        for emoji, role in emojis_roles.items():
            embed.set_author(name="All emoji-role associations", icon_url=ctx.guild.icon_url)
            embed.add_field(name=emoji, value=role)
        await ctx.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if len(roles_msgs) == 0:
            await self.setup_emojis()
        if payload.message_id in roles_msgs:
            role_name = dynamo.get_role(str(payload.emoji))
            if role_name is not None:
                guild = self.bot.get_guild(payload.guild_id)
                user = guild.get_member(payload.user_id)
                role = discord.utils.get(guild.roles, name=role_name)
                await user.add_roles(role, atomic=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if len(roles_msgs) == 0:
            await self.setup_emojis()
        if payload.message_id in roles_msgs:
            role_name = dynamo.get_role(str(payload.emoji))
            if role_name is not None:
                guild = self.bot.get_guild(payload.guild_id)
                user = guild.get_member(payload.user_id)
                role = discord.utils.get(guild.roles, name=role_name)
                try:
                    await user.remove_roles(role, atomic=True)
                except Exception as e:
                    print("couldn't remove role")

    async def setup_emojis(self):
        channel = self.bot.get_channel(roles_chat_id)
        async for message in channel.history(limit=200):
            roles_msgs.append(message.id)


def setup(bot):
    bot.add_cog(AutoRoles(bot))
