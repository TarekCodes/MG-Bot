import discord
import dynamo
import random
from discord.ext import commands

voting_cooldown = 60 * 60

class Rot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="howrot", help="gets the rot percentage of a user")
    async def how_rot(self, ctx, member: discord.Member):
        print(member.id)
        percentage = dynamo.get_rot_score(member.id)
        
        if member.id == 282296769767800835:
            percentage = 0
        if member.id == 199958656337313793:
            percentage = 100
        description = "{} is **{}%** rot".format(member.name, percentage)
        if percentage == 0:
            description = description + " 😳"
        else:
            description = description + " 🤢"
        embed = discord.Embed(description=description)
        embed.set_author(name="Rotting detector")
        await ctx.channel.send(embed=embed)

    @commands.command(name="rotter", help="Tag a rotter")
    @commands.cooldown(1, voting_cooldown , commands.BucketType.user) 
    async def increase_rot(self, ctx, member: discord.Member):
        dynamo.edit_rot_score(member.id, Rot.get_change())
        await ctx.channel.send('Rot score increased!')
        
    @commands.command(name="notrotter", help="Tag someone who never rots")
    @commands.cooldown(1, voting_cooldown, commands.BucketType.user) 
    async def decrease_rot(self, ctx, member: discord.Member):
        dynamo.edit_rot_score(member.id, -Rot.get_change())
        await ctx.channel.send('Rot score decreased!')
        
    @staticmethod
    def get_change():
        return random.randint(1,5)
            
    @increase_rot.error
    @decrease_rot.error
    async def error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Try again after {round(error.retry_after / 60)} minutes")
            
def setup(bot):
    bot.add_cog(Rot(bot))