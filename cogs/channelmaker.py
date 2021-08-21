from discord.ext import commands
from .moderation import is_mod

class ChannelMaker(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.reset()
        self.number_of_teams = 2
        
    @is_mod()
    @commands.command(aliases=['cCate'])
    async def create_category(self, ctx, name):
        if self.guild != None or self.category != None:
            await ctx.send("You have already created a category")
            return
        self.guild = ctx.message.guild
        self.category = await self.guild.create_category(name)
        await ctx.send("Category created!")
       
    @is_mod() 
    @commands.command(aliases=['cChan'])
    async def create_channels(self, ctx, number: int = 1):
        print(self.category)
        if self.guild == None or self.category == None:
            await ctx.send("You must create a category first")
            return
        for _ in range(number):
            match = {}
            for count in range(self.number_of_teams):
                team_label = chr(ord('@') + count + 1)
                print(team_label)
                match[count] = await self.guild.create_voice_channel(f'Match {self.match_number}- team {team_label}',
                                                                     category=self.category,
                                                                     user_limit=self.channel_size)
            self.matches[self.match_number] = match
            self.match_number += 1
        await ctx.send(f'{number} channels made!')

    @is_mod()
    @commands.command(aliases=['dChan'])
    async def delete_channel(self, ctx, match: int = 1):
        if not self.matches.keys().__contains__(match):
            await ctx.send(f'Invalid match number')
            return
        matches = self.matches[match]
        for count in range(self.number_of_teams):
            await matches[count].delete()
        self.matches.pop(match)
        await ctx.send('Match deleted!')
      
    @is_mod()  
    @commands.command(aliases=['dCate'])
    async def delete_category(self, ctx):
        for channel in self.category.voice_channels:
            await channel.delete()
        for channel in self.category.text_channels:
            await channel.delete()
        await self.category.delete()
        self.reset()
        
    @is_mod()
    @commands.command(aliases=['cSize'], help='Set the channel limit size, 0 for unlimited')
    async def change_channel_size(self, ctx, new_size):
        self.channel_size = new_size
        await ctx.send(f'New channel size is {self.channel_size}')
                
    def reset(self):
        self.guild = None
        self.category = None
        self.match_number = 1
        self.matches = {}
        self.channel_size = 0