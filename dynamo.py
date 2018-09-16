import boto3
from boto3.dynamodb.conditions import Key

session = boto3.Session(profile_name='tarek')
dynamodb = session.client('dynamodb')
customTableName = 'mg_custom'
suggestionsTableName = 'mg_suggestions'


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


def add_new_suggestion(message, date):
    table = session.resource('dynamodb').Table(suggestionsTableName)
    table.put_item(Item={
        'user_id': str(message.author.id),
        'date': str(date),
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
