import discord
import dynamo
import random
import requests
import datetime
from datetime import datetime, timedelta
from discord.ext import commands

welcome_chat_id = 334014732572950528
fight_hands = {"rock": "\u270A", "paper": "\u270B", "scissor": "\u270C"}
questions_url = "https://opentdb.com/api.php?amount=1&type=multiple"


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name="fightme")
    async def fight(self, ctx, members: commands.Greedy[discord.Member]):
        author = ctx.author
        for user in members:
            hand, emoji = random.choice(list(fight_hands.items()))
            await ctx.channel.send(user.mention + " played " + hand + " " + emoji)
        hand, emoji = random.choice(list(fight_hands.items()))
        await ctx.channel.send(author.mention + " played " + hand + " " + emoji)

    @commands.command(name="question")
    async def get_question(self, ctx):
        response = requests.get(questions_url).json()
        question = self.decoder(response["results"][0]["question"])
        answer = self.decoder(response["results"][0]["correct_answer"])
        question_id = dynamo.new_question(question, answer)
        await ctx.channel.send("Question #" + str(question_id) + ": " + question)

    @commands.command(name="answer")
    async def answer_question(self, ctx, question_id, *value):
        try:
            answer = " ".join(value)
            correct_answer = dynamo.get_answer(int(question_id))
            if correct_answer is None:
                await ctx.channel.send("Question not found.")
                return
            if correct_answer.strip().lower() == answer.strip().lower():
                dynamo.delete_question(int(question_id))
                score = dynamo.increment_score(ctx.author.id, ctx.guild.id)
                await ctx.message.add_reaction("🌟")
                await ctx.channel.send("Correct answer!!! Your score is now " + str(score))
            else:
                await ctx.message.add_reaction("❌")
                await ctx.channel.send("Wrong answer. Loser.")
        except Exception as e:
            print(e)
            await ctx.channel.send("Invalid command.")

    @commands.command(name="score")
    async def get_score(self, ctx):
        await ctx.channel.send("Your current score is: " + str(dynamo.get_score(ctx.author.id, ctx.guild.id)))

    @commands.command(name="startgiveaway")
    async def start_giveaway(self, ctx, period, prize, mention_everyone: bool, channel_mention: discord.TextChannel):
        mention = ""
        period_unit = period[-1]
        if period_unit.lower() == "d":
            end_date = (datetime.now() + timedelta(days=int(period[:-1]))).strftime("%Y-%m-%d %H:%M:%S")
        else:
            if period_unit.lower() == "h":
                end_date = (datetime.now() + timedelta(hours=int(period[:-1]))).strftime("%Y-%m-%d %H:%M:%S")
            else:
                raise Exception()
        if mention_everyone:
            mention = " @everyone"
        announcement_message = await channel_mention.send(
            "New giveaway! The prize is " + prize + " and it expires " + end_date + ". React to this message with 🏆 to enter!" + mention)
        await announcement_message.add_reaction("🏆")
        dynamo.new_giveaway(announcement_message.id, end_date, prize)

    @commands.command(name="endgiveaway")
    async def end_giveaway(self, ctx, giveaway_id):
        if dynamo.get_giveaway(giveaway_id) is None:
            await ctx.channel.send("Giveaway doesn't exist!")
            return
        winner = dynamo.end_giveaway(giveaway_id)
        if winner is None:
            await ctx.channel.send("No one won. Booooooooo!")
            return
        await ctx.channel.send("The winner is..." + ctx.guild.get_member(int(winner)).mention + "!!!!! Congrats!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith('$'):
            response = dynamo.get_custom_command(message.content[1:])
            if response is not None:
                await message.channel.send(response)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if dynamo.get_giveaway(
                payload.message_id) is not None and payload.emoji.name == "🏆" and payload.user_id != 447970747076575232:
            if dynamo.new_giveaway_entry(payload.user_id, payload.message_id):
                await payload.member.send(
                    "You have been entered in the giveaway. Good luck!")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # handle giveaways
        if dynamo.get_giveaway(payload.message_id) is not None and payload.emoji.name == "🏆":
            dynamo.delete_giveaway_entry(payload.user_id, payload.message_id)
            await self.bot.get_guild(payload.guild_id).get_member(payload.user_id).send(
                "Your entry has been removed.")

    def decoder(self, content):
        new = content.replace("&quot;", "\"").replace("&#039;", "'").replace("&‌pi;", "π").replace("&amp;", "&")
        return new


def setup(bot):
    bot.add_cog(Misc(bot))
