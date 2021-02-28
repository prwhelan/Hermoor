import a2s
import boto3
import botocore
import datetime
from datetime import timezone
import time

SLEEP_DURATION = 5 * 60
awsErrorCount = 0
valheimErrorCount = 0
client = boto3.client('cloudwatch')

# Find the valheim server, probably combine this with heimdallr
serverAddress = boto3.client('ec2').describe_instances(
        Filters=[
            {
                'Name': 'tag:hermoor',
                'Values': [''],
            }
        ])['Reservations'][0]['Instances'][0]['PublicIpAddress']

def publishMetrics(serverName, playerCount):
    try:
        timestamp = datetime.datetime.now(timezone.utc)
        client.put_metric_data(
                Namespace='ValheimDedicated',
                MetricData=[
                    {
                        'MetricName': 'playerCount',
                        'Dimensions': [
                            {
                                'Name': 'serverName',
                                'Value': serverName
                            },
                        ],
                        'Timestamp': timestamp,
                        'Value': playerCount,
                        'Unit': 'Count'
                    },
                ]
            )
        awsErrorCount = 0
    except botocore.exceptions.ClientError as e:
        print("Error calling AWS. RequestId {}, Http {}, Message {}".format(
            e.response['ResponseMetadata']['RequestId'],
            e.response['ResponseMetadata']['HTTPStatusCode'],
            e.response['Error']['Message']))
        awsErrorCount+= 1

# Loop indefinitely, unless for some reason we're chaining errors
while awsErrorCount < 5 and valheimErrorCount < 5:
    try:
        info = a2s.info((serverAddress, 2457))
        valheimErrorCount = 0
        publishMetrics(info.server_name, info.player_count)

    except Exception as e:
        print("Error calling the Valheim Server.")
        valheimErrorCount+= 1
    time.sleep(SLEEP_DURATION)
