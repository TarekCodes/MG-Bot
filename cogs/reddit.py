from discord.ext import commands
import praw
import config
import requests


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reddit")
    async def get_top_post(self, ctx, subreddit, *args):
        try:
            reddit = self.init_reddit()
            subreddit = reddit.subreddit(subreddit)
            period = args[0] if len(args) > 0 else "day"
            index = int(args[1]) if len(args) > 1 else 1
            top = subreddit.top(period)
            for x in range(1, index):
                top.next()
            post = top.next()
        except Exception as e:
            print(e)
            await ctx.channel.send("Invalid Command")
            return
        post_link = config.reddit_url + post.permalink
        if len(post.selftext) > 5:
            await ctx.channel.send(post_link)
            return
        post_json = requests.get(url=post_link[:-1] + ".json", headers={'User-agent': config.clienetID}).json()
        if post.is_video:
            await ctx.channel.send(
                post_json[0]["data"]["children"][0]["data"]["media"]["reddit_video"]["fallback_url"])
            return
        await ctx.channel.send(post_json[0]["data"]["children"][0]["data"]["url"])
        # length = len(post.selftext)
        # if length > 1990:
        #     count = 0
        #     while length > 0:
        #         await message.channel.send("```" + post.selftext[1990 * count:1990 * (count + 1)] + "```")
        #         count += 1
        #         length -= 1990
        #     await message.channel.send("```" + post.selftext[1990 * count:] + "\n\n" + post.shortlink + "```")
        # else:
        #     await message.channel.send("```" + post.selftext + "\n\n" + post.shortlink + "```")

    def init_reddit(self):
        reddit = praw.Reddit(client_id=config.clienetID, client_secret=config.redditSecret, user_agent='discord bot')
        reddit.read_only = True
        return reddit


def setup(bot):
    bot.add_cog(Reddit(bot))
