import discord
import datetime

bot_log = 245252349587619840
voice_role_id = 684253062143016971


async def check_role_change(before, after, client):
    if len(before.roles) == len(after.roles):
        return
    embed = None
    if len(before.roles) > len(after.roles):
        for role in before.roles:
            if role not in after.roles and role.id != voice_role_id:
                embed = discord.Embed(
                    description=after.mention + " **was removed from the** `" + role.name + "` **role**",
                    timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    else:
        for role in after.roles:
            if role not in before.roles and role.id != voice_role_id:
                embed = discord.Embed(description=after.mention + " **was given the** `" + role.name + "` **role**",
                                      timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    try:
        embed.set_author(name=after.display_name, icon_url=after.avatar_url)
        embed.set_footer(text="ID: " + str(after.id))
        await client.get_channel(bot_log).send(embed=embed)
    except Exception as e:
        return
