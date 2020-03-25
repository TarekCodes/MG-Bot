from discord.ext import commands
import dynamo
from .moderation import lead_roles
import requests
import config

events_board_id = "5e611343fd690986ab1187d4"
infra_board_id = "5e611635ed121b4fe3051c0a"
mod_board_id = "5e611428b8c23a2592e3e08a"
social_board_id = "5e6114cb147ff1129f01c217"
infra_suggestion_box_id = "5e602bcbc092ff4343ef6c1f"
events_suggestions_box_id = "5e611343fd690986ab1187d8"
mods_suggestions_box_id = "5e611428b8c23a2592e3e08e"
social_suggestions_box_id = "5e6114cb147ff1129f01c219"
trello_cards_api_prefix = "https://api.trello.com/1/cards"
suggestions_chat_id = 480459932164947969


class Trello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id != suggestions_chat_id or payload.member.top_role.id not in lead_roles:
            return
        suggestion_list = dynamo.get_suggestion(str(payload.message_id))
        if len(suggestion_list) == 0:
            return
        suggestion = suggestion_list[0]
        suggestion_content = suggestion['suggestions'].strip()
        author = self.bot.get_guild(payload.guild_id).get_member(int(suggestion['user_id']))
        emoji = payload.emoji
        cards_list = None
        if emoji.name == "📆":
            cards_list = events_suggestions_box_id
        if emoji.name == "💻":
            cards_list = infra_suggestion_box_id
        if emoji.name == "🏢":
            cards_list = mods_suggestions_box_id
        if emoji.name == "🦸‍♀️":
            cards_list = social_suggestions_box_id
        self.create_card(cards_list, suggestion_content, author.name)

    @staticmethod
    def create_card(list_id, suggestion, author):
        params = {'key': config.trello_key, 'token': config.trello_token, 'idList': list_id,
                  'name': "Suggestion: " + author, 'desc': suggestion}
        requests.post(url=trello_cards_api_prefix, params=params)

    @staticmethod
    async def setup_reactions(msg):
        await msg.add_reaction("📆")
        await msg.add_reaction("💻")
        await msg.add_reaction("🏢")
        await msg.add_reaction("🦸‍♀️")


def setup(bot):
    bot.add_cog(Trello(bot))
