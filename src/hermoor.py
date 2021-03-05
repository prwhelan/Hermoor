import a2s
import boto3
import botocore
import datetime
from datetime import timezone
import time

# When the server is online, run every 5 minutes
SLEEP_DURATION = 5 * 60
# When the server is offline, run every 30 minutes
OFFLINE_SLEEP_DURATION = SLEEP_DURATION * 6
# If we're failing to call AWS, stop trying and wait for manual intervention.
awsErrorCount = 0
client = boto3.client('cloudwatch')

# Find the valheim server, probably combine this with heimdallr
def serverAddress():
    return boto3.client('ec2').describe_instances(
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

# Loop indefinitely, unless for some reason we're chaining errors.
# Only refresh the server IP Address if we failed to call the server.
ipAddress = serverAddress()
while awsErrorCount < 5:
    try:
        info = a2s.info((ipAddress, 2457))
        publishMetrics(info.server_name, info.player_count)
        time.sleep(SLEEP_DURATION)
    except Exception as valheimServerException:
        time.sleep(OFFLINE_SLEEP_DURATION)
        ipAddress = serverAddress()
