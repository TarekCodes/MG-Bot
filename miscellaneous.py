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
