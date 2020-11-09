import discord
import dynamo
import datetime
from datetime import datetime, timedelta
from discord.ext import commands
from dateutil import parser
from .moderation import is_mod
from .trello import Trello

botlog_chat_id = 245252349587619840
suggestions_chat_id = 480459932164947969
default_suggestion_wait = 1
mg_guild_id = 192321256073199616

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @is_mod()
    @commands.command(name="bansuggestions", help="ban user from making suggestions")
    async def ban_suggestions(self, ctx, member_id):
        dynamo.new_suggestion_ban(member_id)
        await ctx.channel.send("Member banned from making suggestions")

    @is_mod()
    @commands.command(name="unbansuggestions", help="unban user from making suggestions")
    async def unban_suggestions(self, ctx, member_id):
        dynamo.suggestion_unban(member_id)
        await ctx.channel.send("Member can make suggestions again")

    @is_mod()
    @commands.command(name="suggestion", help="prints suggestion info in #bot_log")
    async def get_suggestion(self, ctx, message_id):
        suggestion_list = dynamo.get_suggestion(message_id)
        if len(suggestion_list) == 0:
            await ctx.guild.get_channel(botlog_chat_id).send("Suggestion not found")
            return
        suggestion = suggestion_list[0]
        await ctx.guild.query_members(user_ids=[int(suggestion['user_id'])], cache=True)
        member = ctx.guild.get_member(int(suggestion['user_id']))
        embed = discord.Embed(
            description=suggestion['suggestions'].strip(),
            timestamp=parser.parse(suggestion['date']), color=discord.Color.darker_grey())
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.set_footer(text="Suggestion ID: " + message_id)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.guild.get_channel(botlog_chat_id).send(embed=embed)

    @is_mod()
    @commands.command(name="suggestions", help="prints all suggestions by specified user in #bot_log")
    async def get_suggestions(self, ctx, user_id):
        msgs = []
        try:
            suggestions = dynamo.get_all_suggestion(user_id)
            await ctx.guild.query_members(user_ids=[int(user_id)], cache=True)
            current = "```User: " + ctx.guild.get_member(int(user_id)).name + "```\n\n"
            for item in suggestions:
                addition = "```Date: " + item['date'] + "\n" + item['suggestions'].strip() + "```\n\n"
                if len(current + addition) >= 2000:
                    msgs.append(current)
                    current = ""
                current += addition
            msgs.append(current)
            for item in msgs:
                await ctx.guild.get_channel(botlog_chat_id).send(item)
        except Exception as e:
            print(str(e))
            await ctx.channel.send("Invalid Command")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None and message.content.lower().startswith('suggestion: '):
            await self.new_suggestion(message)

    async def new_suggestion(self, message):
        date = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        latest_sugg = dynamo.get_latest_suggestion(message)
        if dynamo.is_suggestion_banned(message.author.id) is not None:
            await message.author.send("You've been banned from making suggestions :(")
            return
        if latest_sugg is not None:
            old_date = datetime.strptime(latest_sugg['date'], "%Y-%m-%d %H:%M:%S")
            date_delta = abs(date - old_date)
            if date_delta.days <= 0 and date_delta.seconds / 3600 < default_suggestion_wait:
                await message.author.send(
                    "Too soon! You need to wait " + str(
                        default_suggestion_wait * 60 - int(date_delta.seconds / 60)) + " minutes.")
                return
        embed = discord.Embed(
            description=message.content[message.content.find(' '):],
            timestamp=datetime.utcnow(), color=discord.Color.light_grey())
        embed.set_author(name="New Suggestion", icon_url=self.bot.get_guild(mg_guild_id).icon_url)
        msg = await self.bot.get_channel(suggestions_chat_id).send(embed=embed)
        dynamo.add_new_suggestion(message, date, msg.id)
        await Trello.setup_reactions(msg)
        await message.author.send("Thanks for your suggestion!")


def setup(bot):
    bot.add_cog(Suggestions(bot))
