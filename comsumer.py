from time import sleep
import boto3
import json
import os
import sys

#command line stuff
thirdParam = ""
if len(sys.argv) > 2:
    print('You have specified too many arguments')
    sys.exit()

if len(sys.argv) == 1:
    print('You have specified too few arguments')
    sys.exit()

if len(sys.argv) == 2:
    if (sys.argv[1] == 's3'):
        thirdParam = sys.argv[1]
    elif (sys.argv[1] == 'dynamo'):
        thirdParam = sys.argv[1]
    else:
        print("enter s3 or dynamo as third parameter")
        sys.exit()


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
        return(key)
    else:
        return None

def deleteWidgetRequests(widgetKey):
    s3.Object('jared-blue-bucket-2', widgetKey).delete()

def createS3(json, widgetKey):
    if((not 'owner' in dict) or (not 'widgetId' in dict)):
        return
    s3.Object('jared-blue-bucket-3', 'widgets/' + json['owner'] + '/' + json['widgetId']).put()

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
    
    
    print(json['otherAttributes'][0])

    table.put_item(Item=item)
    print()


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


def main():
    while True:
        print('got here lol')
        sleep(.1)
        try:
            widgetGetRequest(checkForWidgetRequests())
        except:
             print("An exception occurred")

main()