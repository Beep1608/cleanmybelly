import json

def handler(event, context):
    print("Received event:", json.dumps(event))
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "message": "Hello World from cleanmybelly dev backend!",
            "status": "online"
        })
    }
