from expiringdict import ExpiringDict

welcome_cache_max_size : int = 50
# Duration in minutes
welcome_cache_duration : float = 20
welcome_message_cache : ExpiringDict = ExpiringDict(max_len=welcome_cache_max_size, max_age_seconds=60*welcome_cache_duration)

def add_welcome_message(user_id : int, message_id : int):
    """Add a user's welcome message when they join

    Parameters
    ----------
    user_id : int
        The user's ID
    message_id : int
        The ID of the welcome message
    """
    welcome_message_cache[user_id] = message_id

def get_welcome_message_id(user_id : int):
    """Get the ID of the welcome message for the user specified

    Parameters
    ----------
    user_id : int
        The user's ID

    Returns
    -------
    int
        The ID of the message that welcomed this user
    """
    message_id = welcome_message_cache.get(user_id, None)
    welcome_message_cache.pop(user_id)
    return message_id
