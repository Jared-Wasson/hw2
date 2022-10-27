import logging
from time import sleep
import boto3
import json
import os
import sys

s3Client = boto3.client('s3')
s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

my_bucket2 = s3.Bucket('jared-blue-bucket-2')

def checkForWidgetRequests():
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

def deleteWidgetRequests(widgetKey):
    s3.Object('jared-blue-bucket-2', widgetKey).delete()
    logging.info('widget request sucessfully deleted')

def createS3(json, widgetKey):
    # if((not json['owner']) or (not json['widgetId'])):
    #     return
    s3.Object('jared-blue-bucket-3', 'widgets/' + json['owner'] + '/' + json['widgetId']).put()
    logging.info('widget sucessfully put in s3 bucket 3')

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

def widgetGetRequest(widgetKey):
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
