import discord
import datetime

bot_log = 245252349587619840
voice_role_id = 684253062143016971
color_url_prefix = "https://www.color-hex.com/color/"


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


async def check_nickname_change(before, after, client):
    try:
        if len(before.nick) == len(after.nick):
            return
    except Exception as e:
        return
    embed = discord.Embed(
        description=after.mention + " **Nickname Changed**",
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.set_author(name="{}#{}".format(after.name, after.discriminator), icon_url=after.avatar_url)
    embed.set_footer(text="ID: " + str(after.id))
    embed.add_field(name="Before",
                    value=before.nick,
                    inline=False)
    embed.add_field(name="After",
                    value=after.nick,
                    inline=False)
    await client.get_channel(bot_log).send(embed=embed)


async def member_join_log(member, client):
    embed = discord.Embed(
        description=member.mention + " {}#{}".format(member.name, member.discriminator),
        timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
    embed.set_author(name="Member Joined", icon_url=member.avatar_url)
    embed.set_footer(text="ID: " + str(member.id))
    embed.set_thumbnail(url=member.avatar_url)
    await client.get_channel(bot_log).send(embed=embed)


async def member_leave_log(member, client):
    embed = discord.Embed(
        description=member.mention + " {}#{}".format(member.name, member.discriminator),
        timestamp=datetime.datetime.utcnow(), color=discord.Color.red())
    embed.set_author(name="Member Left", icon_url=member.avatar_url)
    embed.set_footer(text="ID: " + str(member.id))
    embed.set_thumbnail(url=member.avatar_url)
    await client.get_channel(bot_log).send(embed=embed)


async def member_ban_log(user, client):
    embed = discord.Embed(
        description=user.mention + " {}#{}".format(user.name, user.discriminator),
        timestamp=datetime.datetime.utcnow(), color=discord.Color.red())
    embed.set_author(name="Member Banned", icon_url=user.avatar_url)
    embed.set_footer(text="ID: " + str(user.id))
    embed.set_thumbnail(url=user.avatar_url)
    await client.get_channel(bot_log).send(embed=embed)


async def member_unban_log(user, client):
    embed = discord.Embed(
        description=user.mention + " {}#{}".format(user.name, user.discriminator),
        timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.set_author(name="Member Unbanned", icon_url=user.avatar_url)
    embed.set_footer(text="ID: " + str(user.id))
    embed.set_thumbnail(url=user.avatar_url)
    await client.get_channel(bot_log).send(embed=embed)


async def channel_create_log(channel, client):
    embed = discord.Embed(
        description="**Channel Created: #{}**".format(channel.name),
        timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
    embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon_url)
    embed.set_footer(text="ID: " + str(channel.id))
    await client.get_channel(bot_log).send(embed=embed)


async def channel_delete_log(channel, client):
    embed = discord.Embed(
        description="**Channel Deleted: #{}**".format(channel.name),
        timestamp=datetime.datetime.utcnow(), color=discord.Color.red())
    embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon_url)
    embed.set_footer(text="ID: " + str(channel.id))
    await client.get_channel(bot_log).send(embed=embed)


async def role_create_log(role, client):
    embed = discord.Embed(description=":crossed_swords:** Role Created: {}**".format(role.name),
                          timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
    embed.set_footer(text="ID: " + str(role.id))
    embed.add_field(name="Permissions", value=get_perms(list(filter(filter_perms, iter(role.permissions)))))
    await client.get_channel(bot_log).send(embed=embed)


async def role_delete_log(role, client):
    embed = discord.Embed(description=":wastebasket: ** Role Deleted: {}**".format(role.name),
                          timestamp=datetime.datetime.utcnow(), color=discord.Color.red())
    embed.set_footer(text="ID: " + str(role.id))
    embed.add_field(name="Color",
                    value="[{}]({}{})".format(str(role.color), color_url_prefix, str(role.color).replace("#", "")),
                    inline=False)
    embed.add_field(name="Permissions", value=get_perms(list(filter(filter_perms, iter(role.permissions)))))
    await client.get_channel(bot_log).send(embed=embed)


def filter_perms(perm):
    return perm[1]


def get_perms(perms):
    perms_list = ""
    for perm in perms:
        if perms_list != "":
            perms_list += ", "
        perms_list += (perm[0])
    perms_list = perms_list.replace("_", " ")
    return perms_list
