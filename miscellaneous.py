import discord
import datetime
from datetime import datetime
import dynamo

default_suggestion_wait = 1


async def invite_link(message):
    await message.channel.send("https://discord.gg/ErTb8t3")
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
    msg += "\n**$invitelink** (prints an invite to MG)"
    msg += "\n**$custom <command> <msg to be sent>** (creates/updates a custom command)"
    msg += "\n**$custom <command>** (deletes an existing command)"
    msg += "\n**$mutechannel** (mutes everyone except for mods)"
    msg += "\n**$unmutechannel** (brings the channel back to how it was)"
    msg += "\n**$suggestion <msg_id>** (prints suggestion info in #bot_log)"
    msg += "\n**$suggestions <user_id>** (prints all user suggestions in #bot_log)"
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
    try:
        if len(parsed) < 2:
            raise Exception()
        suggestions = dynamo.get_all_suggestion(parsed[1])
        print(parsed[1])
        message = "```User: " + message.guild.get_member(int(parsed[1])).name + "\n\n"
        for item in suggestions:
            message += "Date: " + item['date'] + "\n" + item['suggestions'].strip() + "\n\n\n"
        message += '```'
        await client.get_channel(bot_log).send(message)
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
