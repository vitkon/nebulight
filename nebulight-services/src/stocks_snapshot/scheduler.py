import os
import time
import boto3
import json

def handler(event, context):
    client = boto3.client('stepfunctions')
    state_machine_arn = os.getenv('STATE_MACHINE_ARN')
    market = event.get('market', 'US')  # Default to 'US' if not provided
    
    input={ "market": market }

    response = client.start_execution(
        stateMachineArn=state_machine_arn,
        name='Execution-' + str(int(time.time())),
        input=json.dumps(input)
    )
    return response
