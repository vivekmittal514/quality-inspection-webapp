import json
import boto3
from datetime import datetime
import os
import base64
import ast
from decimal import Decimal

# Custom JSON encoder to handle Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
runtime_sm = boto3.client('sagemaker-runtime')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def invoke_sagemaker_endpoint(image_bytes):
    """
    Call SageMaker endpoint for image analysis
    """
    try:
        print(f"Image bytes length: {len(image_bytes)}")
        
        response = runtime_sm.invoke_endpoint(
            EndpointName=os.environ['SAGEMAKER_ENDPOINT_NAME'],
            ContentType='application/x-image',
            Body=image_bytes
        )
    
        response_body = response['Body'].read()
        if isinstance(response_body, bytes):
            response_body = response_body.decode('utf-8')
            
        print(f"Raw response from SageMaker: {response_body}")
        
        try:
            import ast
            result = ast.literal_eval(response_body)
            
            if isinstance(result, (list, tuple)):
                if len(result) >= 2:
                    status = str(result[0])
                    confidence = Decimal(str(result[1]))
                else:
                    raise ValueError(f"Insufficient values in response: {result}")
            else:
                status = str(result)
                confidence = Decimal('1.0')
            
            return {
                'status': status.strip('"'),
                'confidence': confidence,
                'raw_prediction': 1 if status.strip('"').lower() == 'good' else 0,
                'raw_response': response_body
            }
            
        except (ValueError, SyntaxError) as e:
            print(f"Failed to parse response: {response_body}")
            print(f"Parse error: {str(e)}")
            
            try:
                parts = response_body.split(',')
                status = parts[0].strip('"')
                confidence = Decimal(str(parts[1])) if len(parts) > 1 else Decimal('1.0')
                
                return {
                    'status': status,
                    'confidence': confidence,
                    'raw_prediction': 1 if status.lower() == 'good' else 0,
                    'raw_response': response_body
                }
            except Exception as e2:
                print(f"Fallback parsing failed: {str(e2)}")
                raise Exception(f"Could not parse SageMaker response: {response_body}")
        
    except Exception as e:
        print(f"Error calling SageMaker endpoint: {str(e)}")
        raise

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }
    try:
        print("Received event:", event)
        
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        elif isinstance(event.get('body'), dict):
            body = event['body']
        else:
            raise ValueError("Invalid request body format")
            
        print("Parsed body:", body)
        
        bucket_name = os.environ['BUCKET_NAME']
        
        if 'imageKey' not in body:
            raise KeyError("imageKey is required in the request body")
            
        image_key = body['imageKey']
        
        print(f"Getting image {image_key} from bucket {bucket_name}")
        response = s3.get_object(Bucket=bucket_name, Key=image_key)
        image_bytes = response['Body'].read()
        
        print("Calling SageMaker endpoint for analysis")
        analysis_result = invoke_sagemaker_endpoint(image_bytes)
        print(f"Analysis result: {analysis_result}")
        
        # Store the result in DynamoDB
        item = {
            'imageKey': image_key,
            'status': analysis_result['status'],
            'confidence': analysis_result['confidence'],
            'rawPrediction': analysis_result['raw_prediction'],
            'uploadDate': datetime.utcnow().isoformat(),
            'imageUrl': f"https://{bucket_name}.s3.amazonaws.com/{image_key}"
        }
        
        print(f"Storing analysis result in DynamoDB: {item}")
        table.put_item(Item=item)
        
        # Use DecimalEncoder for JSON serialization
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'imageKey': image_key,
                'status': analysis_result['status'],
                'confidence': str(analysis_result['confidence']),  # Convert Decimal to string
                'imageUrl': item['imageUrl']
            }, cls=DecimalEncoder)  # Use the custom encoder
        }
        
    except KeyError as e:
        print(f"Missing required field: {str(e)}")
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': f"Missing required field: {str(e)}"})
        }
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in request body: {str(e)}")
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f"Error processing request: {str(e)}"})
        }
