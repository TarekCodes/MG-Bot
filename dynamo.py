import boto3

session = boto3.Session(profile_name='tarek')
dynamodb = session.client('dynamodb')
tableName = 'mg_custom'


def init():
    try:
        dynamodb.describe_table(TableName=tableName)
    except Exception:
        table = dynamodb.create_table(
            TableName=tableName,
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
        dynamodb.get_waiter('table_exists').wait(TableName=tableName)


def add_custom_command(command, value):
    table = session.resource('dynamodb').Table(tableName)
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
    table = session.resource('dynamodb').Table(tableName)
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