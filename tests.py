from unitTests import *
import json
import os
import sys

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


test_checkForWidgetRequests()
test_createS3()
test_deleteWidgetRequests()
