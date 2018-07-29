import discord
import dynamo


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
    msg += "\n**$umutechannel** (brings the channel back to how it was)"
    await message.channel.send(msg)
