import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

session = boto3.Session(profile_name='tarek')
dynamodb = session.client('dynamodb')
customTableName = 'mg_custom'
suggestionsTableName = 'mg_suggestions'
questionsTableName = 'mg_questions'
scoresTableName = 'mg_scores'
suggestionBansTableName = 'mg_suggestion_bans'
phraseTableName = 'mg_phrase'
phrase_cache = {}


def init():
    try:
        dynamodb.describe_table(TableName=customTableName)
    except Exception:
        table = dynamodb.create_table(
            TableName=customTableName,
            KeySchema=[
                {
                    'AttributeName': 'command',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'command',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Table not found")
        dynamodb.get_waiter('table_exists').wait(TableName=customTableName)

    try:
        dynamodb.describe_table(TableName=suggestionBansTableName)
    except Exception:
        table = dynamodb.create_table(
            TableName=suggestionBansTableName,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Table not found")
        dynamodb.get_waiter('table_exists').wait(TableName=suggestionBansTableName)

    try:
        dynamodb.describe_table(TableName=suggestionsTableName)
    except Exception:
        table = dynamodb.create_table(
            TableName=suggestionsTableName,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'date',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'date',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Table not found")
        dynamodb.get_waiter('table_exists').wait(TableName=suggestionsTableName)

    try:
        dynamodb.describe_table(TableName=questionsTableName)
    except Exception:
        table = dynamodb.create_table(
            TableName=questionsTableName,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Table not found")
        dynamodb.get_waiter('table_exists').wait(TableName=questionsTableName)

    try:
        dynamodb.describe_table(TableName=scoresTableName)
    except Exception:
        table = dynamodb.create_table(
            TableName=scoresTableName,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Table not found")
        dynamodb.get_waiter('table_exists').wait(TableName=questionsTableName)

    try:
        dynamodb.describe_table(TableName=phraseTableName)
    except Exception:
        table = dynamodb.create_table(
            TableName=phraseTableName,
            KeySchema=[
                {
                    'AttributeName': 'phrase',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'phrase',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Table not found")
        dynamodb.get_waiter('table_exists').wait(TableName=customTableName)
    scan_for_phrases()


def add_custom_command(command, value):
    table = session.resource('dynamodb').Table(customTableName)
    if value == "":
        table.delete_item(
            Key={
                'command': command,
            }
        )
        return "deleted"
    table.put_item(Item={
        'command': command,
        'value': value
    })
    return "done"


def get_custom_command(command):
    table = session.resource('dynamodb').Table(customTableName)
    response = table.get_item(
        Key={
            'command': command
        }
    )
    try:
        value = response['Item']['value']
        return value
    except Exception:
        print("not found")
        return None


def add_new_suggestion(message, date, msg_id):
    table = session.resource('dynamodb').Table(suggestionsTableName)
    table.put_item(Item={
        'user_id': str(message.author.id),
        'date': str(date),
        'msg_id': str(msg_id),
        'suggestions': message.content[message.content.find(' '):]
    })
    return "done"


def get_latest_suggestion(message):
    table = session.resource('dynamodb').Table(suggestionsTableName)
    last_suggestion = table.query(
        KeyConditionExpression=Key('user_id').eq(str(message.author.id))
    )
    if len(last_suggestion['Items']) == 0:
        return None
    return last_suggestion['Items'][len(last_suggestion['Items']) - 1]


def get_all_suggestion(user_id):
    table = session.resource('dynamodb').Table(suggestionsTableName)
    last_suggestion = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )
    return last_suggestion['Items']


def get_suggestion(msg_id):
    table = session.resource('dynamodb').Table(suggestionsTableName)
    suggestion = table.query(
        IndexName='msg_id_index',
        KeyConditionExpression=Key('msg_id').eq(msg_id)
    )
    return suggestion['Items']


def get_all_custom():
    result = []
    current = ""
    table = session.resource('dynamodb').Table(customTableName)
    items = table.scan()
    for custom in items['Items']:
        addition = "```" + custom['command'] + "\t" + custom['value'] + "```"
        if len(current + addition) >= 2000:
            result.append(current)
            current = ""
        current += addition
    result.append(current)
    return result


def new_question(question, answer):
    table = session.resource('dynamodb').Table(questionsTableName)
    question_id = datetime.now().microsecond
    table.put_item(Item={
        'id': question_id,
        'question': question,
        'answer': answer
    })
    return question_id


def get_answer(question_id):
    try:
        table = session.resource('dynamodb').Table(questionsTableName)
        response = table.get_item(
            Key={
                'id': question_id
            }
        )
        answer = response['Item']['answer']
        return answer
    except Exception:
        return None


def delete_question(question_id):
    table = session.resource('dynamodb').Table(questionsTableName)
    table.delete_item(
        Key={
            'id': question_id,
        }
    )
    return "deleted"


def increment_score(message):
    table = session.resource('dynamodb').Table(scoresTableName)
    user_id = str(message.guild.id) + "_" + str(message.author.id)
    try:
        response = table.get_item(
            Key={
                'id': user_id
            }
        )
        new_score = response['Item']['score'] + 1
        table.put_item(Item={
            'id': user_id,
            'score': new_score,
        })
        return new_score
    except Exception:
        table.put_item(Item={
            'id': user_id,
            'score': 1,
        })
        return 1


def get_score(message):
    table = session.resource('dynamodb').Table(scoresTableName)
    user_id = str(message.guild.id) + "_" + str(message.author.id)
    try:
        response = table.get_item(
            Key={
                'id': user_id
            }
        )
        return response['Item']['score']
    except Exception:
        table.put_item(Item={
            'id': user_id,
            'score': 0,
        })
        return 0


def new_suggestion_ban(user_id):
    table = session.resource('dynamodb').Table(suggestionBansTableName)
    table.put_item(Item={
        'user_id': str(user_id),
    })
    return "done"


def is_suggestion_banned(user_id):
    try:
        table = session.resource('dynamodb').Table(suggestionBansTableName)
        response = table.get_item(
            Key={
                'user_id': str(user_id)
            }
        )
        found = response['Item']['user_id']
        return found
    except Exception as e:
        print(e)
        return None


def suggestion_unban(user_id):
    table = session.resource('dynamodb').Table(suggestionBansTableName)
    table.delete_item(
        Key={
            'user_id': user_id,
        }
    )
    return "deleted"


def add_phrase(phrase, value):
    table = session.resource('dynamodb').Table(phraseTableName)
    if value == "":
        table.delete_item(
            Key={
                'phrase': phrase,
            }
        )
        return "deleted"
    table.put_item(Item={
        'phrase': phrase,
        'value': value
    })
    scan_for_phrases()
    return "done"


def get_phrase(phrase):
    if phrase in phrase_cache:
        return phrase_cache[phrase]
    return None


def scan_for_phrases():
    table = session.resource('dynamodb').Table(phraseTableName)
    response = table.scan()
    for i in response['Items']:
        phrase_cache[i['phrase']] = i['value']
