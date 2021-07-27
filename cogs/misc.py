import discord
import dynamo
import random
import requests
import datetime
from datetime import datetime, timedelta
from discord.ext import commands
from .moderation import is_mod
import typing

welcome_chat_id = 334014732572950528
fight_hands = {"rock": "\u270A", "paper": "\u270B", "scissor": "\u270C"}
questions_url = "https://opentdb.com/api.php?amount=1&type=multiple"
eid_present_url = "https://i.imgur.com/H9lriCz.png"


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autoreactlist = {}

    @commands.command(name="invitelink", help="Prints a single use invite that expires after 24hrs")
    async def invite_link(self, ctx):
        invite = await ctx.guild.get_channel(welcome_chat_id).create_invite(max_uses=1, max_age=1440,
                                                                            reason="created by " + str(ctx.author))
        await ctx.channel.send("New invite created for " + ctx.author.mention + " " + invite.url)

    @commands.command(name="autoreact", help="Auto-react to every message a user sends with specified emojis")
    async def auto_react(self, ctx, member, *emojis: typing.Union[discord.Emoji, str]):
        result_emojis = []
        for emoji in emojis:
            result_emojis.append(emoji)
        self.autoreactlist[member] = result_emojis
        await ctx.channel.send("Auto reaction added!")

    @commands.command(name="deleteautoreact", help="Delete auto-reacts")
    async def delete_auto_react(self, ctx, member):
        if member in self.autoreactlist:
            del self.autoreactlist[member]
            await ctx.channel.send("Auto reaction deleted!")
        else:
            await ctx.channel.send("User didn't have an auto reaction.")

    @is_mod()
    @commands.command(help="creates/updates a custom command")
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

    @is_mod()
    @commands.command(name="getallcustom", help="prints all custom commands currently configured")
    async def get_all_custom(self, ctx):
        response = dynamo.get_all_custom()
        for msg in response:
            await ctx.channel.send(msg)

    @commands.command(name="fightme", help="simulates a rock-paper-scissors game between people to solve problems :D")
    async def fight(self, ctx, members: commands.Greedy[discord.Member]):
        count = 1
        hand, emoji = random.choice(list(fight_hands.items()))
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name="NEW BATTLE!!", icon_url=ctx.guild.icon_url)
        for user in members:
            embed.add_field(name="Fighter #{}".format(count),
                            value=user.mention + " played **" + hand + "** " + emoji, inline=False)
            count += 1
            hand, emoji = random.choice(list(fight_hands.items()))
        embed.add_field(name="Fighter #{}".format(count),
                        value=ctx.author.mention + " played **" + hand + "** " + emoji, inline=False)
        await ctx.channel.send(embed=embed)

    @commands.command(name="trivia", help="sends a random trivia questions in the chat")
    async def get_question(self, ctx):
        response = requests.get(questions_url).json()
        question = self.decoder(response["results"][0]["question"])
        answer = self.decoder(response["results"][0]["correct_answer"])
        choices = response["results"][0]["incorrect_answers"]
        decoded_choices = []
        for choice in choices:
            decoded_choices.append(self.decoder(choice))
        decoded_choices.append(answer)
        random.shuffle(decoded_choices)
        answer_num = decoded_choices.index(answer) + 1
        question_id = dynamo.new_question(question, choices, answer_num)
        embed = discord.Embed(color=discord.Color.purple(), description="**" + question + "**")
        embed.set_author(name="Question #{}".format(question_id), icon_url=ctx.guild.icon_url)
        count = 1
        for choice in decoded_choices:
            embed.add_field(name="Choice #{}".format(count),
                            value=choice, inline=False)
            count += 1
        await ctx.channel.send(embed=embed)

    @commands.command(name="answer", help="answers a trivia question by providing the question number and answer")
    async def answer_question(self, ctx, question_id: int, answer: int):
        correct_answer = dynamo.get_answer(question_id)
        if correct_answer is None:
            await ctx.channel.send("Question not found.")
            return
        if answer == correct_answer:
            dynamo.delete_question(question_id)
            score = dynamo.increment_score(ctx.author.id, ctx.guild.id)
            await ctx.message.add_reaction("🌟")
            embed = discord.Embed(color=discord.Color.green(), description="Correct Answer!")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name="New Score", value=score)
            await ctx.channel.send(embed=embed)
        else:
            await ctx.message.add_reaction("❌")
            await ctx.channel.send("Wrong answer. Loser.")

    @commands.command(name="score", help="gets your current trivia score")
    async def get_score(self, ctx):
        await ctx.channel.send("Your current score is: " + str(dynamo.get_score(ctx.author.id, ctx.guild.id)))

    @commands.command(name="howrot", help="gets the rot percentage of a user")
    async def how_rot(self, ctx, member: discord.Member):
        percentage = random.randint(0, 100)
        if member.id == 282296769767800835:
            percentage = 0
        if member.id == 199958656337313793:
            percentage = 100
        description = "{} is **{}%** rot".format(member.name, percentage)
        if percentage == 0:
            description = description + " 😳"
        else:
            description = description + " 🤢"
        embed = discord.Embed(description=description)
        embed.set_author(name="Rotting detector")
        await ctx.channel.send(embed=embed)

    @is_mod()
    @commands.command(name="startgiveaway", help="starts a new giveaway")
    async def start_giveaway(self, ctx, period, mention_everyone: bool, channel: discord.TextChannel, *prize):
        prize = ' '.join(prize)
        mention = ""
        period_unit = period[-1]
        period_name = "Days"
        if period_unit.lower() == "d":
            end_date = (datetime.now() + timedelta(days=int(period[:-1]))).strftime("%Y-%m-%d %H:%M:%S")
        else:
            if period_unit.lower() == "h":
                end_date = (datetime.now() + timedelta(hours=int(period[:-1]))).strftime("%Y-%m-%d %H:%M:%S")
                period_name = "Hours"
            else:
                raise Exception()
        if mention_everyone:
            mention = " @everyone"

        embed = discord.Embed(
            description="React to this message with 🏆 to enter!",
            timestamp=datetime.utcnow(), color=discord.Color.gold())
        embed.set_author(name="NEW GIVEAWAY!", icon_url=ctx.guild.icon_url)
        embed.add_field(name="Expires",
                        value="In {} {}".format(period[:-1], period_name))
        embed.add_field(name="Prize",
                        value=prize, inline=False)
        embed.set_thumbnail(url=eid_present_url)
        msg = await channel.send(mention, embed=embed)
        embed.set_footer(text="ID: " + str(msg.id))
        await msg.edit(embed=embed)
        await msg.add_reaction("🏆")
        dynamo.new_giveaway(msg.id, end_date, prize)

    @is_mod()
    @commands.command(name="endgiveaway", help="returns a winner and ends the giveaway early if necessary")
    async def end_giveaway(self, ctx, giveaway_id):
        if dynamo.get_giveaway(giveaway_id) is None:
            await ctx.channel.send("Giveaway doesn't exist!")
            return
        winner = dynamo.end_giveaway(giveaway_id)
        if winner is None:
            await ctx.channel.send("No one won. Booooooooo!")
            return
        await ctx.guild.query_members(user_ids=[int(winner)], cache=True)
        await ctx.channel.send("The winner is..." + ctx.guild.get_member(int(winner)).mention + "!!!!! Congrats!")

    @is_mod()
    @commands.command(name="phrase", help="creates/updates a custom msg when a phrase is sent")
    async def new_phrase(self, ctx, phrase, *value):
        value = " ".join(value)
        if dynamo.add_phrase(phrase, value) == "deleted":
            await ctx.channel.send("Phrase deleted!")
        else:
            await ctx.channel.send("Mission Accomplished")

    @commands.command(name="rng", help="Returns a random number within a range")
    async def rng(self, ctx, start: int, end: int):
        num = random.randint(start, end)
        await ctx.channel.send(num)

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.check_auto_react(message)
        if message.author.id == self.bot.user.id:
            return
        if message.content.startswith('$'):
            response = dynamo.get_custom_command(message.content[1:])
            if response is not None:
                await message.channel.send(response)
        else:
            val = dynamo.get_phrase(message.content)
            if val is not None:
                await message.channel.send(val)
                return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if dynamo.get_giveaway(
                payload.message_id) is not None and payload.emoji.name == "🏆" and payload.user_id != self.bot.user.id:
            if dynamo.new_giveaway_entry(payload.user_id, payload.message_id):
                await payload.member.send(
                    "You have been entered in the giveaway. Good luck!")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if dynamo.get_giveaway(payload.message_id) is not None and payload.emoji.name == "🏆":
            dynamo.delete_giveaway_entry(payload.user_id, payload.message_id)
            await self.bot.get_guild(payload.guild_id).query_members(user_ids=[payload.user_id], cache=True)
            await self.bot.get_guild(payload.guild_id).get_member(payload.user_id).send(
                "Your entry has been removed.")

    @staticmethod
    def decoder(content):
        new = content.replace("&quot;", "\"").replace("&#039;", "'").replace("&‌pi;", "π").replace("&amp;", "&") \
            .replace("&auml;", "ä")
        return new

    async def check_auto_react(self, message):
        if str(message.author.id) in self.autoreactlist:
            for emoji in self.autoreactlist[str(message.author.id)]:
                await message.add_reaction(emoji)


def setup(bot):
    bot.add_cog(Misc(bot))
