import discord
import datetime
from datetime import datetime
import dynamo
import requests

default_suggestion_wait = 1
url = "https://opentdb.com/api.php?amount=1&type=multiple"


async def invite_link(message, client, welcome_chat):
    invite = await client.get_channel(welcome_chat).create_invite(max_uses=1, max_age=1440,
                                                                  reason="created by " + str(message.author))
    await message.channel.send("New invite created for " + message.author.mention + " " + invite.url)
    return


async def custom(message):
    try:
        parsed = message.content.split()
        if len(parsed) < 2:
            raise Exception()
        command = parsed[1]
        value = ""
        for part in parsed[2:]:
            value += part + " "
        if dynamo.add_custom_command(command, value) == "deleted":
            await message.channel.send("Command deleted!")
        else:
            await message.channel.send("Mission Accomplished")
    except Exception as e:
        print(e)
        await message.channel.send("Invalid Command")
    return


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
    await message.channel.send(msg)


async def new_suggestion(message, client, suggestions_chat):
    date = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    latest_sugg = dynamo.get_latest_suggestion(message)
    if latest_sugg is not None:
        old_date = datetime.strptime(latest_sugg['date'], "%Y-%m-%d %H:%M:%S")
        date_delta = abs(date - old_date)
        if date_delta.days <= 0 and date_delta.seconds / 3600 < default_suggestion_wait:
            await message.author.send(
                "Too soon! You need to wait " + str(
                    default_suggestion_wait * 60 - int(date_delta.seconds / 60)) + " minutes.")
            return
    msg = await client.get_channel(suggestions_chat).send(
        "New Suggestion: " + message.content[message.content.find(' '):])
    dynamo.add_new_suggestion(message, date, msg.id)
    await message.author.send("Thanks for your suggestion!")
    return


async def get_suggestions(message, client, bot_log):
    parsed = message.content.split()
    msgs = []
    try:
        if len(parsed) < 2:
            raise Exception()
        suggestions = dynamo.get_all_suggestion(parsed[1])
        print(parsed[1])
        current = "```User: " + message.guild.get_member(int(parsed[1])).name + "```\n\n"
        for item in suggestions:
            addition = "```Date: " + item['date'] + "\n" + item['suggestions'].strip() + "```\n\n"
            if len(current + addition) >= 2000:
                msgs.append(current)
                current = ""
            current += addition
        msgs.append(current)
        for item in msgs:
            await client.get_channel(bot_log).send(item)
    except Exception as e:
        print(str(e))
        await message.channel.send("Invalid Command")


async def get_suggestion(message, client, bot_log):
    parsed = message.content.split()
    try:
        if len(parsed) < 2:
            raise Exception()
        suggestion_list = dynamo.get_suggestion(parsed[1])
        if len(suggestion_list) == 0:
            await client.get_channel(bot_log).send("Suggestion not found")
            return
        suggestion = suggestion_list[0]
        message = "```User: " + message.guild.get_member(int(suggestion['user_id'])).name + "\n\n"
        message += "Date: " + suggestion['date'] + "\n" + suggestion['suggestions'].strip() + "\n\n\n"
        message += '```'
        await client.get_channel(bot_log).send(message)
    except Exception as e:
        print(str(e))
        await message.channel.send("Invalid Command")


async def get_question(message):
    response = requests.get(url).json()
    question = decoder(response["results"][0]["question"])
    answer = decoder(response["results"][0]["correct_answer"])
    question_id = dynamo.new_question(question, answer)
    await message.channel.send("Question #" + str(question_id) + ": " + question)


async def answer_question(message):
    try:
        parsed = message.content.split()
        if len(parsed) < 2:
            raise Exception()
        question_id = parsed[1]
        answer = ""
        for part in parsed[2:]:
            answer += part + " "
        correct_answer = dynamo.get_answer(int(question_id))
        if correct_answer is None:
            await message.channel.send("Question not found.")
            return
        if correct_answer.strip().lower() == answer.strip().lower():
            dynamo.delete_question(int(question_id))
            score = dynamo.increment_score(message)
            await message.add_reaction("🌟")
            await message.channel.send("Correct answer!!! Your score is now " + str(score))
        else:
            await message.add_reaction("❌")
            await message.channel.send("Wrong answer. Loser.")
    except Exception as e:
        print(e)
        await message.channel.send("Invalid command.")
    return


async def get_score(message):
    await message.channel.send("Your current score is: " + str(dynamo.get_score(message)))


def decoder(content):
    new = content.replace("&quot;", "\"").replace("&#039;", "'").replace("&‌pi;", "π").replace("&‌amp;", "&")
    return new
