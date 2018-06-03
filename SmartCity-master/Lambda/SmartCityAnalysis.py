import boto3
import json
import os

# Initiate Firehose client
firehose_client = boto3.client('firehose')


def lambda_handler(event, context):
    records = []
    batch = []
    try:
        # TODO: write code...
        for record in event['Records']:
            Car = {}
            lineId = record['dynamodb']['Keys']['laneId']['S']
            h = record['dynamodb']['Keys']['hour']['S']
            numOfCar = str(record['dynamodb']['NewImage']['noOfCar']['N'])

            t_stats = '{ "lineId":"%s", "hour":"%s", "numOfCar":"%s" }\n' \
                      % (lineId, \
                         h, \
                         numOfCar
                         )
            print("Done")

            Car["Data"] = t_stats
            records.append(Car)
        batch.append(records)
        res = firehose_client.put_record_batch(
            DeliveryStreamName='Sample1',
            Records=batch[0]
        )
        return 'Successfully processed {} records.'.format(len(event['Records']))

    except Exception as e:
        pass
