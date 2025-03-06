import json
import boto3
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def lambda_handler(event, context):
    try:
        response = table.scan()
        items = response['Items']
        
        # Sort items by uploadDate in descending order
        items.sort(key=lambda x: x['uploadDate'], reverse=True)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'items': items}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
