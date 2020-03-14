async def help(message):
    msg = "**$cone <@user1> <@user2> ...**"
    msg += "\n**$uncone <@user1> <@user2> ...**"
    msg += "\n**$mute <@user1> <@user2> ...**"
    msg += "\n**$unmute <@user1> <@user2> ...**"
    msg += "\n**$servermute <@user1> <@user2> ...** (server-wide mute)"
    msg += "\n**$serverunmute <@user1> <@user2> ...** (server-wide unmute)"
    msg += "\n**$clear <#> <@user>** (optionally specify a user to only target him/her)"
    msg += "\n**$invitelink** (Prints a single use invite that expires after 24hrs)"
    msg += "\n**$custom <command> <msg to be sent>** (creates/updates a custom command)"
    msg += "\n**$custom <command>** (deletes an existing command)"
    msg += "\n**$getallcustom** (prints all custom commands currently configured)"
    msg += "\n**$mutechannel** (mutes everyone except for mods)"
    msg += "\n**$unmutechannel** (brings the channel back to how it was)"
    msg += "\n**$suggestion <msg_id>** (prints suggestion info in #bot_log)"
    msg += "\n**$suggestions <user_id>** (prints all suggestions by specified user in #bot_log)"
    msg += "\n**$reddit <sub-reddit> <period> <#>** (gets top post or whatever number if period is specified)"
    msg += "\n**$bansuggestions <user_id>** (ban user from making suggestions)"
    msg += "\n**$unbansuggestions <user_id>** (unban user from making suggestions)"
    msg += "\n**$question** (sends a random trivia questions in the chat)"
    msg += "\n**$answer <question #> <answer>** (answers a trivia question by providing the question number and answer)"
    msg += "\n**$score** (gets your current trivia score)"
    msg += "\n**$fightme <@user>** (simulates a rock-paper-scissors game between 2 people to solve problems :D)"
    msg += "\n**$startgiveaway <period (#d or #h)> <prize> <true or false to mention everyone> " \
           "<channel for announcement> ** (starts a new giveaway, default channel is the current one)"
    msg += "\n**$endgiveaway <giveaway msg ID>** (returns a winner and ends the giveaway early if necessary)"
    msg += "\n**$phrase <\"phrase\"> <msg to be sent>** (creates/updates a custom msg when a phrase is sent)"

    await message.channel.send(msg)


