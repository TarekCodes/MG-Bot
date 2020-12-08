import discord
import dynamo
import datetime
from datetime import datetime
from discord.ext import commands
from dateutil import parser
from .moderation import is_mod

botlog_chat_id = 245252349587619840
questions_chat_id = 749067051372642345
default_question_wait = 1
mg_guild_id = 192321256073199616


class Questions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @is_mod()
    @commands.command(name="banquestions", help="ban user from asking questions")
    async def ban_questions(self, ctx, member_id):
        dynamo.anon_questions_ban(member_id)
        await ctx.channel.send("Member banned from asking questions")

    @is_mod()
    @commands.command(name="unbanquestions", help="unban user from asking questions")
    async def unban_questions(self, ctx, member_id):
        dynamo.anon_questions_unban(member_id)
        await ctx.channel.send("Member can ask questions again")

    @is_mod()
    @commands.command(name="question", help="prints question info in #bot_log")
    async def get_question(self, ctx, message_id):
        questions_list = dynamo.get_anon_question(message_id)
        if len(questions_list) == 0:
            await ctx.guild.get_channel(botlog_chat_id).send("Question not found")
            return
        question = questions_list[0]
        await ctx.guild.query_members(user_ids=[int(question['user_id'])], cache=True)
        member = ctx.guild.get_member(int(question['user_id']))
        embed = discord.Embed(
            description=question['questions'].strip(),
            timestamp=parser.parse(question['date']), color=discord.Color.darker_grey())
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.set_footer(text="Question ID: " + message_id)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.guild.get_channel(botlog_chat_id).send(embed=embed)

    @is_mod()
    @commands.command(name="questions", help="prints all questions by specified user in #bot_log")
    async def get_questions(self, ctx, user_id):
        msgs = []
        try:
            questions = dynamo.get_all_anon_questions(user_id)
            await ctx.guild.query_members(user_ids=[int(user_id)], cache=True)
            current = "```User: " + ctx.guild.get_member(int(user_id)).name + "```\n\n"
            for item in questions:
                addition = "```Date: " + item['date'] + "\n" + item['questions'].strip() + "```\n\n"
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
        if message.guild is None and message.content.lower().startswith('question: '):
            await self.new_question(message)

    async def new_question(self, message):
        date = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        latest_question = dynamo.get_latest_anon_question(message)
        if dynamo.is_anon_questions_banned(message.author.id) is not None:
            await message.author.send("You've been banned from asking questions :(")
            return
        if latest_question is not None:
            old_date = datetime.strptime(latest_question['date'], "%Y-%m-%d %H:%M:%S")
            date_delta = abs(date - old_date)
            if date_delta.days <= 0 and date_delta.seconds / 3600 < default_question_wait:
                await message.author.send(
                    "Too soon! You need to wait " + str(
                        default_question_wait * 60 - int(date_delta.seconds / 60)) + " minutes.")
                return
        embed = discord.Embed(
            description=message.content[message.content.find(' '):],
            timestamp=datetime.utcnow(), color=discord.Color.light_grey())
        embed.set_author(name="New Question", icon_url=self.bot.get_guild(mg_guild_id).icon_url)
        msg = await self.bot.get_channel(questions_chat_id).send(embed=embed)
        dynamo.add_anon_question(message, date, msg.id)
        await message.author.send("Thanks for your question!")


def setup(bot):
    bot.add_cog(Questions(bot))
