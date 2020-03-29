from discord.ext import commands
import praw
import config
import requests
import discord
from .moderation import is_mod

reddit_url = "https://reddit.com"
reddit_icon_url = "https://www.redditstatic.com/desktop2x/img/favicon/favicon-96x96.png"


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @is_mod()
    @commands.command(name="reddit", help="gets top post or whatever number if period is specified")
    async def get_top_post(self, ctx, subreddit, *args):
        reddit = self.init_reddit()
        period = args[0] if len(args) > 0 else "day"
        index = int(args[1]) if len(args) > 1 else 1
        subreddit = reddit.subreddit(subreddit)
        top = subreddit.top(period)
        for x in range(1, index):
            top.next()
        post = top.next()
        if subreddit.over18 or post.over_18:
            await ctx.channel.send("NSFW posts not allowed.")
            return
        post_link = reddit_url + post.permalink
        embed = discord.Embed(color=discord.Color.orange())
        embed.set_author(name=subreddit.display_name, icon_url=reddit_icon_url)
        embed.description = "[{}]({})".format(post.title, post_link)
        if post.is_self:
            embed.add_field(name="Content", value=post.selftext, inline=False)
        else:
            if "v.redd.it" not in str(post.url):
                embed.set_image(url=post.url)
            else:
                video_url = \
                    requests.get(url=post_link[:-1] + ".json", headers={'User-agent': config.clientID}).json()[0][
                        "data"][
                        "children"][0]["data"]["media"]["reddit_video"]["fallback_url"]
                embed.add_field(name="Direct Video URL", value=video_url, inline=False)
        embed.add_field(name="Upvote Ratio", value=str(int(float(post.upvote_ratio) * 100)) + "%")
        embed.add_field(name="Number of Comments", value=post.num_comments)
        await ctx.channel.send(embed=embed)

    @staticmethod
    def init_reddit():
        reddit = praw.Reddit(client_id=config.clientID, client_secret=config.redditSecret, user_agent='discord bot')
        reddit.read_only = True
        return reddit


def setup(bot):
    bot.add_cog(Reddit(bot))
