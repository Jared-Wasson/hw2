import logging
from time import sleep
import boto3
import json
import os
import sys

logging.basicConfig(filename="logfilename.log", level=logging.INFO)
#command line
thirdParam = ""
pullFromS3 = True
if len(sys.argv) > 3:
    print('You have specified too many arguments')
    sys.exit()

if len(sys.argv) == 1:
    print('You have specified too few arguments')
    sys.exit()

if len(sys.argv) == 2:
    if (sys.argv[1] == 's3'):
        thirdParam = sys.argv[1]
        logging.info('set to send to s3')
    elif (sys.argv[1] == 'dynamo'):
        thirdParam = sys.argv[1]
        logging.info('set to send to dynamo')
    else:
        print("enter s3 or dynamo as third parameter")
        sys.exit()

if len(sys.argv) == 3:
    if(sys.argv[2] == 'cs5260-requests'):
        pullFromS3 = False
        logging.info('pulling from cs5260-requests')



s3Client = boto3.client('s3')
s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sqs = boto3.client('sqs', region_name='us-east-1')
queue_url = 'https://sqs.us-east-1.amazonaws.com/514149339831/cs5260-requests'

my_bucket2 = s3.Bucket('jared-blue-bucket-2')

def checkForWidgetRequests():
    if (pullFromS3):
        widgetsInBucket = []
        key = ""
        for file in my_bucket2.objects.all():
            widgetsInBucket.append(file.key)

        for file in widgetsInBucket:
            if (key == ""):
                key = file
            if (file < key):
                key = file

        if(len(widgetsInBucket)):
            logging.info('widget key sent to get processed')
            return(key)
        else:
            return None
    else:
        #pull from queue
        response = sqs.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']

        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        return message


def deleteWidgetRequests(widgetKey):
    s3.Object('jared-blue-bucket-2', widgetKey).delete()
    logging.info('widget request sucessfully deleted')

def createS3(jsons, widgetKey):
    # if((not json['owner']) or (not json['widgetId'])):
    #     return
    s3.Object('jared-blue-bucket-3', 'widgets/' + jsons['owner'] + '/' + jsons['widgetId']).put(Body=json.dumps(jsons))
    logging.info('widget sucessfully put in s3 bucket 3')


def deleteS3(json, widgetKey):
    s3.Object('jared-blue-bucket-3', 'widgets/' + json['owner'] + '/' + json['widgetId']).delete()


def createDynamo(json):
    table = dynamodb.Table('myTable')
    #build item obj
    item = {}
    for i in json:

        if (i == 'otherAttributes'):
            for j in range(len(json['otherAttributes'])-1):
                json['otherAttributes'][j]
                for x in json['otherAttributes'][j-1]:
                    item[x] = json['otherAttributes'][j][x]
        else:
            item[i] = json[i]

    table.put_item(Item=item)
    logging.info('widget sucessfully put in dynamo table')

def deleteDynamo(json ,widgetKey):
    table = dynamodb.Table('myTable')
    table.delete_item(Key={'widgetId': json['widgetId']})

def updateDynamo(jsons):
    data = jsons
    table = dynamodb.Table('myTable')
    del data['type']
    del data['owner']
    widgetId = data['widgetId']
    del data['widgetId']
    updateExpression = ['set ']
    updateAttributeValues = dict()
    for key, value in data.items():
        updateExpression.append(f" {key} = :{key},")
        updateAttributeValues[f":{key}"] = value

    expression, values =  "".join(updateExpression)[:-1], updateAttributeValues

    table.update_item(
        Key = {'widgetId': widgetId},
        UpdateExpression = expression,
        ExpressionAttributeValues = values
    )

def widgetGetRequestS3(widgetKey):
    if (widgetKey == None):
        return
    s3Client.download_file('jared-blue-bucket-2', widgetKey, './' + widgetKey + '.json')
    deleteWidgetRequests(widgetKey)

    with open('./' + widgetKey + '.json') as f:
        data = json.load(f)

    obj = data
    if(obj['type']):
        if(obj['type'] == 'create'):
            if(thirdParam == "s3"):
                createS3(obj, widgetKey)
            else: 
                createDynamo(obj)
        elif (obj['type'] == 'delete'):
            if(thirdParam == "s3"):
                deleteS3(obj, widgetKey)
            else:
                deleteDynamo(obj, widgetKey)

        elif (obj['type'] == 'update'):
            if(thirdParam == "s3"):
                createS3(obj, widgetKey)
            else:
                updateDynamo(obj)

def widgetGetRequestSQS(message):
    dict_json = json.loads(message['Body'])
    if( dict_json['type']):
        if( dict_json['type'] == 'create'):
            if(thirdParam == "s3"):
                createS3( dict_json, 0)
            else: 
                createDynamo( dict_json)

def main():
    # value = 100
    # while value != 0:
    #     value = value -1
    #     sleep(.1)
    #     try:
    #         widgetGetRequest(checkForWidgetRequests())
    #     except:
    #         print('error occured')
    if(pullFromS3):
        widgetGetRequestS3(checkForWidgetRequests())
    else:
        widgetGetRequestSQS(checkForWidgetRequests())

main()