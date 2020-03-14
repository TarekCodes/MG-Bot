from discord.ext import commands
import discord

roleEmojis = {}
customRoleEmojis = {}
roles_msgs = []
roles_chat_id = 365624761398591489


class AutoRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup_emojis()
        # await self.set_up_roles_msg()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in roles_msgs:
            guild = self.bot.get_channel(payload.channel_id).guild
            user = guild.get_member(payload.user_id)
            role_name = roleEmojis.get(payload.emoji.name, None)
            if role_name is not None:
                role = discord.utils.get(guild.roles, name=role_name)
                await user.add_roles(role, atomic=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id in roles_msgs:
            guild = self.bot.get_channel(payload.channel_id).guild
            user = guild.get_member(payload.user_id)
            role_name = roleEmojis.get(payload.emoji.name, None)
            if role_name is not None:
                role = discord.utils.get(guild.roles, name=role_name)
                try:
                    await user.remove_roles(role, atomic=True)
                except Exception as e:
                    print("couldn't remove role")

    async def set_up_roles_msg(self):
        rules_channel = self.bot.get_channel(roles_chat_id)
        for emoji in roleEmojis:
            for current_msg in roles_msgs:
                msg = await rules_channel.fetch_message(current_msg)
                try:
                    if emoji in customRoleEmojis:
                        await msg.add_reaction(self.bot.get_emoji(customRoleEmojis.get(emoji)))
                    else:
                        await msg.add_reaction(emoji)
                    break
                except Exception as e:
                    print('next msg')

    def setup_emojis(self):
        roleEmojis["🃏"] = "Road Blockers"
        roleEmojis["chickenleg"] = "PUBG Crew"
        roleEmojis["🐉"] = "League of Losers"
        roleEmojis["🏹"] = "Hanzo Mains"
        roleEmojis["🔫"] = "Rush B Watch Cat"
        roleEmojis["💀"] = "Dead by Daylight"
        roleEmojis["⚛"] = "Ancient Defenders"
        roleEmojis["⚽"] = "Learning to Dribble"
        roleEmojis["💠"] = "Guardians"
        roleEmojis["🛠"] = "Master Builders"
        roleEmojis["🐛"] = "Stick Fightin"
        roleEmojis["⛳"] = "Mini Golf Rules"
        roleEmojis["🌈"] = "Fuzing Hostage"
        roleEmojis["🎵"] = "music haramis"
        roleEmojis["runescape"] = "Osbuddies"
        roleEmojis["⚔"] = "Dauntless"
        roleEmojis["💸"] = "Cheap Gamers"
        roleEmojis["🗺"] = "Skribblio"
        roleEmojis["🔷"] = "Paladins"
        roleEmojis["🤺"] = "For Honor"
        roleEmojis["🎣"] = "World of Warcraft"
        roleEmojis["🎇"] = "StarCraft"
        roleEmojis["🕋"] = "Lecture"
        roleEmojis["🤖"] = "TennoFrame"
        roleEmojis["🐊"] = "Monster Hunters"
        roleEmojis["🔄"] = "Nintendo Switch"
        roleEmojis["🤠"] = "The Steves"
        roleEmojis["⛓"] = "Sirat-ul-Exile"
        roleEmojis["🔰"] = "Keyboard Warriors"
        roleEmojis["🐸"] = "Fascist Scum"
        roleEmojis["🏳"] = "Farm Simulator"
        roleEmojis["👊🏾"] = "Button Mashers"
        roleEmojis["🎮"] = "Apex Legends"
        roleEmojis["🇱"] = "League of Losers EU"
        roleEmojis["⚔"] = "Hodor"
        roleEmojis["👷🏾"] = "Rainbow Six Siege"
        roleEmojis["😇"] = "Halo"
        roleEmojis["🌠"] = "Stormtrooper"
        roleEmojis["💳"] = "Tarnoobz"
        roleEmojis["⚠"] = "Going Dark"
        roleEmojis["🍿"] = "Coke and Popcorn"

        customRoleEmojis["chickenleg"] = 319229845957640192
        customRoleEmojis["runescape"] = 455087244898992129

        roles_msgs.append(398539277035896846)
        roles_msgs.append(458465086693048341)
        roles_msgs.append(460218391781965824)
        roles_msgs.append(633304992719306762)


def setup(bot):
    bot.add_cog(AutoRoles(bot))
