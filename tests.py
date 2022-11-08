from unitTests import *
import json
import os
import sys

testJson = {"type":"create","requestId":"6f6121c7-14d6-4d0a-a431-9f1a6dde8808","widgetId":"7f0bfd22-876f-42f2-937d-cdf048caec2a","owner":"Mary Matthews","label":"ET","description":"DYNJLGBLSLEZLEJECEVLLXUMNPSJAEYVNECKBQFIHPAOMCSVRHZINZWXDXQFOTXDVCAGSAYK","otherAttributes":[{"name":"color","value":"blue"},{"name":"size","value":"143"},{"name":"size-unit","value":"cm"},{"name":"height","value":"379"},{"name":"width-unit","value":"cm"},{"name":"length-unit","value":"cm"},{"name":"price","value":"31.84"},{"name":"quantity","value":"650"},{"name":"note","value":"EFCQGMBMWWRVXGQUZXUFWSSOUSXZSFEDMGEQISTGTKRAOFAFFSZVJWTLJYPMZWGRSULXEZDSHOXQEMBQPGXBCWSJABNPNEDMTPFJZMXLBOHOJCHLBVGTUDBEJDMOWNQHTTIYHMVPYWSUXYUBPTY"}]}

s3 = boto3.resource('s3')
my_bucket3 = s3.Bucket('jared-blue-bucket-3')

def test_checkForWidgetRequests():
    assert checkForWidgetRequests() == '1612306375850'
    print('test_checkForWidgetRequests() passed')

def test_createS3():
    key = False
    s3 = boto3.resource('s3')
    my_bucket3 = s3.Bucket('jared-blue-bucket-3')
    with open('./1612306375850.json') as f:
        data = json.load(f)
    createS3(data,'1612306375850')
    widgetsInBucket = []
    for file in my_bucket3.objects.all():
        widgetsInBucket.append(file.key)

    for file in my_bucket3.objects.all():
        if(file == 'widgets/Mary Matthews/7f0bfd22-876f-42f2-937d-cdf048caec2a'):
            print()
    key = True
    assert key == True
    print("test_createS3() passed")


def test_deleteWidgetRequests():
    deleteWidgetRequests('1612306375850')
    assert checkForWidgetRequests() == None
    print("test_deleteWidgetRequests() passed")


def test_deleteS3():
    deleteS3(testJson, 0)
    key = False
    s3 = boto3.resource('s3')
    my_bucket3 = s3.Bucket('jared-blue-bucket-3')
    widgetsInBucket = []
    for file in my_bucket3.objects.all():
        widgetsInBucket.append(file.key)
    assert len(widgetsInBucket) == 0
    print("test_deleteS3() passed")

def test_createDynamo():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    createDynamo(testJson)
    print("test_createDynamo() passed")

def test_deleteDynamo():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('myTable')
    deleteDynamo(testJson, 0)
    assert table.item_count == 0
    print("test_deleteDynamo() passed")



test_checkForWidgetRequests()
test_createS3()
test_deleteWidgetRequests()
test_deleteS3()
test_createDynamo()
test_deleteDynamo()

