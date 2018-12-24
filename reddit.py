import praw
import config
import requests


def init_reddit():
    reddit = praw.Reddit(client_id=config.clienetID, client_secret=config.redditSecret, user_agent='discord bot')
    reddit.read_only = True
    return reddit


async def get_top_post(message):
    try:
        parsed = message.content.split()
        if len(parsed) < 2:
            raise Exception()
        reddit = init_reddit()
        subreddit = reddit.subreddit(parsed[1])
        period = parsed[2] if len(parsed) > 2 else "day"
        index = int(parsed[3]) if len(parsed) > 3 else 1
        top = subreddit.top(period)
        for x in range(1, index):
            top.next()
        post = top.next()
    except Exception as e:
        await message.channel.send("Invalid Command")
        return
    post_link = config.reddit_url + post.permalink
    if len(post.selftext) > 5:
        await message.channel.send(post_link)
        return
    post_json = requests.get(url=post_link[:-1] + ".json", headers={'User-agent': config.clienetID}).json()
    if post.is_video:
        await message.channel.send(post_json[0]["data"]["children"][0]["data"]["media"]["reddit_video"]["fallback_url"])
        return
    await message.channel.send(post_json[0]["data"]["children"][0]["data"]["url"])
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
