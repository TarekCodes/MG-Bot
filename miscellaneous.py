import discord
import datetime
from datetime import datetime, timedelta
import dynamo
import requests
import random

default_suggestion_wait = 1


async def help(message):
    msg = "**$cone <@user1> <@user2> ...**"
    msg += "\n**$uncone <@user1> <@user2> ...**"
    msg += "\n**$mute <@user1> <@user2> ...**"
    msg += "\n**$unmute <@user1> <@user2> ...**"
    msg += "\n**$servermute <@user1> <@user2> ...** (server-wide mute)"
    msg += "\n**$serverunmute <@user1> <@user2> ...** (server-wide unmute)"
    msg += "\n**$clear <#> <@user>** (optionally specify a user to only target him/her)"
    msg += "\n**$invitelink** (Prints a single use invite that expires after 24hrs)"
    msg += "\n**$custom <command> <msg to be sent>** (creates/updates a custom command)"
    msg += "\n**$custom <command>** (deletes an existing command)"
    msg += "\n**$getallcustom** (prints all custom commands currently configured)"
    msg += "\n**$mutechannel** (mutes everyone except for mods)"
    msg += "\n**$unmutechannel** (brings the channel back to how it was)"
    msg += "\n**$suggestion <msg_id>** (prints suggestion info in #bot_log)"
    msg += "\n**$suggestions <user_id>** (prints all suggestions by specified user in #bot_log)"
    msg += "\n**$reddit <sub-reddit> <period> <#>** (gets top post or whatever number if period is specified)"
    msg += "\n**$bansuggestions <user_id>** (ban user from making suggestions)"
    msg += "\n**$unbansuggestions <user_id>** (unban user from making suggestions)"
    msg += "\n**$question** (sends a random trivia questions in the chat)"
    msg += "\n**$answer <question #> <answer>** (answers a trivia question by providing the question number and answer)"
    msg += "\n**$score** (gets your current trivia score)"
    msg += "\n**$fightme <@user>** (simulates a rock-paper-scissors game between 2 people to solve problems :D)"
    msg += "\n**$startgiveaway <period (#d or #h)> <prize> <true or false to mention everyone> " \
           "<channel for announcement> ** (starts a new giveaway, default channel is the current one)"
    msg += "\n**$endgiveaway <giveaway msg ID>** (returns a winner and ends the giveaway early if necessary)"
    msg += "\n**$phrase <\"phrase\"> <msg to be sent>** (creates/updates a custom msg when a phrase is sent)"

    await message.channel.send(msg)


async def new_phrase(message):
    try:
        message_content = message.content
        start = message_content.find("\"")
        end = message_content.find("\"", start + 1)
        value = message_content[end + 1:]
        phrase = message_content[start + 1:end]
        if dynamo.add_phrase(phrase, value) == "deleted":
            await message.channel.send("Phrase deleted!")
        else:
            await message.channel.send("Mission Accomplished")
    except Exception as e:
        print(e)
        await message.channel.send("Invalid Command")
    return


async def start_giveaway(message):
    try:
        parsed = message.content.split()
        channel_mention = message.channel
        if len(message.channel_mentions) >= 1:
            channel_mention = message.channel_mentions[0]
        period = parsed[1]
        prize = parsed[2]
        mention_everyone = parsed[3]
        mention = ""
        if mention_everyone.lower() != "true" and mention_everyone.lower() != "false":
            print(mention_everyone.lower())
            raise Exception("not equal")
        period_unit = period[-1]
        if period_unit.lower() == "d":
            end_date = (datetime.now() + timedelta(days=int(period[:-1]))).strftime("%Y-%m-%d %H:%M:%S")
        else:
            if period_unit.lower() == "h":
                end_date = (datetime.now() + timedelta(hours=int(period[:-1]))).strftime("%Y-%m-%d %H:%M:%S")
            else:
                raise Exception()
        if mention_everyone == "true":
            mention = " @everyone"
        announcement_message = await channel_mention.send(
            "New giveaway! The prize is " + prize + " and it expires " + end_date + ". React to this message with 🏆 to enter!" + mention)
        await announcement_message.add_reaction("🏆")
        dynamo.new_giveaway(announcement_message.id, end_date, prize)
    except Exception as e:
        print(e)
        await message.channel.send("Invalid Command")


async def end_giveaway(client, message):
    try:
        parsed = message.content.split()
        giveaway_id = parsed[1]
        if dynamo.get_giveaway(giveaway_id) is None:
            await message.channel.send("Giveaway doesn't exist!")
            return
        winner = dynamo.end_giveaway(giveaway_id)
        if winner is None:
            await message.channel.send("No one won. Booooooooo!")
            return
        await message.channel.send("The winner is..." + client.get_user(int(winner)).mention + "!!!!! Congrats!")
    except Exception as e:
        print(e)
        await message.channel.send("Invalid Command")
