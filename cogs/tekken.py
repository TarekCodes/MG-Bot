from discord.ext import commands
import discord
import json
import os
import random

CHARACTER_NAMES = [
    {
        "name": "armor_king",
        "alias": ["armor", "ak"]
    },
    {
        "name": "devil_jin",
        "alias": ["dj", "dvj", "djin", "devil", "deviljin"]
    },
    {
        "name": "dragunov",
        "alias": ["sergei", "drag", "dragu"]
    },
    {
        "name": "fahkumram",
        "alias": ["fakumram", "fakuram", "faku", "fukurmom", "fak", "fuck", "fahk"]
    },
    {
        "name": "ganryu",
        "alias": ["ganruy", "ganny", "sumo"]
    },
    {
        "name": "geese",
        "alias": ["goose"]
    },
    {
        "name": "hwoarang",
        "alias": ["hwo", "who", "hwoa"]
    },
    {
        "name": "jack7",
        "alias": ["jack", "jack-7", "jaska"]
    },
    {
        "name": "julia",
        "alias": ["julle"]
    },
    {
        "name": "lucky_chloe",
        "alias": ["chloe", "lucky", "lc"]
    },
    {
        "name": "heihachi",
        "alias": ["hei", "hessu", "heiska"]
    },
    {
        "name": "katarina",
        "alias": ["kata", "kat"]
    },
    {
        "name": "kazuya",
        "alias": ["kaz", "kazze"]
    },
    {
        "name": "kuma",
        "alias": ["panda", "karhu"]
    },
    {
        "name": "marduk",
        "alias": ["mara", "mardug", "marduck"]
    },
    {
        "name": "master_raven",
        "alias": ["master", "raven", "masterraven", "mraven", "maven"]
    },
    {
        "name": "noctis",
        "alias": ["nocto"]
    },
    {
        "name": "paul",
        "alias": ["pave", "pole"]
    },
    {
        "name": "shaheen",
        "alias": ["sha", "suhina", "shaclean"]
    },
    {
        "name": "yoshimitsu",
        "alias": ["yoshi"]
    },
    {
        "name": "xiaoyu",
        "alias": ["ling"]
    }
]

MOVE_TYPES = {'ra': 'Rage art',
              'rage_art': 'Rage art',
              'rd': 'Rage drive',
              'rage_drive': 'Rage drive',
              'wb': 'Wall bounce',
              'wall_bounce': 'Wall bounce',
              'ts': 'Tail spin',
              'tail_spin': 'Tail spin',
              'screw': 'Tail spin',
              'homing': 'Homing',
              'homari': 'Homing',
              'armor': 'Power crush',
              'armori': 'Power crush',
              'pc': 'Power crush',
              'power': 'Power crush',
              'power_crush': 'Power crush'}


class Tekken(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="fetches move types or a specific move")
    async def tekken(self, ctx, chara_name, *move_name):
        move_name = " ".join(move_name)
        chara_alias = list(filter(lambda x: (chara_name in x['alias']), CHARACTER_NAMES))
        if chara_alias:
            chara_name = chara_alias[0]['name']
        character = self.get_character(chara_name)

        if character is not None:
            if move_name.lower() in MOVE_TYPES:
                move_name = move_name.lower()
                move_list = self.get_by_move_type(character, MOVE_TYPES[move_name])
                if len(move_list) < 1:
                    embed = self.error_embed(
                        'No ' + MOVE_TYPES[move_name].lower() + ' for ' + character.get('proper_name'))
                    await ctx.channel.send(embed=embed)
                elif len(move_list) == 1:
                    move = self.get_move(character, move_list[0])
                    embed = self.move_embed(character, move)
                    msg = await ctx.channel.send(embed=embed)
                elif len(move_list) > 1:
                    embed = self.move_list_embed(character, move_list, MOVE_TYPES[move_name])
                    msg = await ctx.channel.send(embed=embed)
            else:
                move = self.get_move(character, move_name)
                if move:
                    embed = self.move_embed(character, move)
                    msg = await ctx.channel.send(embed=embed)
                else:
                    embed = self.error_embed('Move not found: ' + move_name)
                    msg = await ctx.channel.send(embed=embed)

        else:
            bot_msg = 'Character ' + chara_name + ' does not exist.'
            embed = self.error_embed(bot_msg)
            msg = await ctx.channel.send(embed=embed)

    @commands.command(name="tekkenRandom", help="returns a random Tekken character")
    async def tekkenRandom(self, ctx):
        chara_name = random.choice(CHARACTER_NAMES).get('name')
        character = self.get_character(chara_name)
        embed = self.character_random_embed(character)
        await ctx.channel.send(embed=embed)

    @staticmethod
    def get_character(chara_name):
        filepath = 'data/character_misc.json'
        with open(filepath) as chara_misc_file:
            contents = chara_misc_file.read()
        chara_misc_json = json.loads(contents)
        chara_details = list(filter(lambda x: (x['name'].lower() == chara_name.lower()), chara_misc_json))
        if not chara_details:
            return None
        return chara_details[0]

    @staticmethod
    def get_by_move_type(character, move_type):
        move_list = []
        filepath = 'data/' + character.get('local_json')
        with open(filepath) as move_file:
            move_file_contents = move_file.read()
        move_json = json.loads(move_file_contents)
        moves = list(filter(lambda x: (move_type.lower() in x['Notes'].lower()), move_json))
        for move in moves:
            move_list.append(move['Command'])
        return move_list

    @staticmethod
    def get_move(character, move_command):
        filepath = 'data/' + character.get('local_json')
        with open(filepath) as move_file:
            move_file_contents = move_file.read()
        move_json = json.loads(move_file_contents)

        move = list(filter(lambda x: (x['Command'] == move_command), move_json))
        if len(move) > 0:
            return move[0]
        move = list(filter(lambda x: (Tekken.move_simplifier(x['Command'].lower())
                                      == Tekken.move_simplifier(move_command.lower())), move_json))
        if not move:
            return None
        return move[0]

    @staticmethod
    def error_embed(err):
        return discord.Embed(title='Error',
                             colour=0xFF4500,
                             description=err)

    @staticmethod
    def move_embed(character, move):
        embed = discord.Embed(title=character['proper_name'],
                              colour=0x00EAFF,
                              url=character['online_webpage'],
                              description='Move: ' + move['Command'])
        embed.set_thumbnail(url=character['portrait'])
        embed.add_field(name='Property', value=move['Hit level'])
        embed.add_field(name='Damage', value=move['Damage'])
        embed.add_field(name='Startup', value='i' + move['Start up frame'])
        embed.add_field(name='Block', value=move['Block frame'])
        embed.add_field(name='Hit', value=move['Hit frame'])
        embed.add_field(name='Counter Hit', value=move['Counter hit frame'])
        embed.add_field(name='Notes', value=move['Notes'])
        return embed

    @staticmethod
    def move_list_embed(character, move_list, move_type):
        desc_string = ''
        for move in move_list:
            desc_string += move + '\n'
        embed = discord.Embed(title=character['proper_name'] + ' ' + move_type.lower() + ':',
                              colour=0x00EAFF,
                              description=desc_string)
        return embed

    @staticmethod
    def character_random_embed(character):
        proper_name = character['proper_name']
        character_link = character['online_webpage']
        embed = discord.Embed(title='Your random character is',
                              colour=0x00EAFF,
                              description=f'[{proper_name}]({character_link})')
        embed.set_thumbnail(url=character['portrait'])
        return embed

    @staticmethod
    def move_simplifier(move_input):
        move_replacements = {
            'fff': 'f,f,f',
            'ff': 'f,f',
            'bf': 'b,f',
            'fb': 'f,b',
            'ddf': 'd,df',
            'cd': 'f,n,d,df',
            'wr': 'f,f,f',
            'ewgf': 'f,n,d,df+2'
        }

        # Don't apply the above replacements for any of the moves with the following notation
        replacements_blacklist = ["cds"]

        for move in move_replacements:
            if not any([mv in move_input for mv in replacements_blacklist]) and move in move_input:
                move_input = move_input.replace(move, move_replacements[move])

        move_input = move_input.replace(' ', '')
        move_input = move_input.replace('/', '')
        move_input = move_input.replace('+', '')

        return move_input


def setup(bot):
    bot.add_cog(Tekken(bot))
