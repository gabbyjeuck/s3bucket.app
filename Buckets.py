#Buckets.py
#Name: Gabrielle Jeuck

#Class: SDEV 400 - Homework 1

#IMPORTS
from datetime import datetime
from pytz import timezone
import boto3 
from botocore.exceptions import ClientError
import botocore
import logging
import re

#CREATES BUCKET RETURNS TRUE IF SO OTHERWISE FALSE - MENU OPTION 1
def create_bucket(bucket_name, region=None):
    try:
        #default region is  us-east-1 if None.
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True
    
#PUTS OBJECT IN ALREADY CREATED BUCKET RETURNS TRUE IF SO OTHERWISE FALSE - MENU OPTION 2
def object_to_previous_bucket(bucket_name, filename):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(filename, bucket_name, filename)
    except FileNotFoundError:
        print('File was not found try again')
        return False
    return True
    
#DELETES OBJECT FROM BUCKET RETURNS TRUE IF DEL OTHERWISE FALSE - MENU OPTION 3
def delete_object(bucket_name, object_name):
    s3 = boto3.client('s3')
    try:
        s3.delete_object(Bucket=bucket_name, Key=object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
    
#DELETES BUCKET FROM s3 RETURNS TRUE IF DELETED OTHERWISE FALSE - MENU OPTION 4
def delete_bucket(bucket_name):
    s3 = boto3.client('s3')
    try:
        s3.delete_bucket(Bucket=bucket_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
    
#COPIES OBJECT TO OTHER BUCKET - MENU OTPION 5
def copy_object_to_bucket(src_bucket_name, src_object_name, 
                            dest_bucket_name, dest_object_name=None):
    copy_source = {'Bucket': src_bucket_name, 'Key': src_object_name}
    if dest_object_name is None:
        dest_object_name = src_object_name
    s3 = boto3.client('s3')
    try:
        s3.copy_object(CopySource=copy_source, Bucket=dest_bucket_name, 
                                Key=dest_object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
    
#DOWNLOADS ITEM FROM BUCKET - MENU OPTION 6
def download_bucket(bucket_name, key):
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(bucket_name).download_file(key, key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist")
        else: 
            raise

#CHECKS IF BUCKET EXISTS RETURNS TRUE IF SO OTHERWISE FALSE
def bucket_exists(bucket_name):
    s3 = boto3.client('s3')
    try:
        response = s3.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        logging.debug(e)
        return False
    return True
    
#LISTS BUCKETS AVAILABLE 
def list_buckets_available():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    string_buckets = "Bucket List: %s" % buckets
    return string_buckets

#LISTS ITEMS AVAILABLE IN BUCKETS
def list_items_available(bucket_name):
    s3 = boto3.client('s3')
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
    except ClientError as e:
        logging.error(e)
        return None
    try:
        return response['Contents']
    except KeyError:
        print('There are no contents in this bucket, please choose another option.')
        menu()
        
#Returns date/time after user quits
def time():
    #Current time/date with US Pacific as timezone
    date_object = datetime.now()
    date_object_PST = date_object.astimezone(timezone('US/Pacific'))
    #formats date mm/dd/yy
    str_date = date_object_PST.strftime("%x")
    #formats time 24HOUR:minute:seconds
    str_time = date_object_PST.strftime("%H:%M:%S")
    str_date_time = "Date: " + str_date + "\nTime: " +str_time +" US/Pacific"
    return str_date_time        

#Returns user_selection for menu
def user_selection():
    user_selection = int(input("\nPlease Enter Options 1-7 from menu: "))
    return user_selection

#MAIN MENU 
def menu():
    print('Select from the menu option to customize Buckets')
    print('1. Create bucket')
    print('2. Put object in already created bucket')
    print('3. Delete an object in a bucket')
    print('4. Delete a bucket')
    print('5. Copy an object from one bucket to another')
    print('6. Download an existing object from a bucket')
    print('7. Exit the program')
    notQuit = True
    #prompts user until users chooses to quit
    logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(asctime)s: %(message)s')
    #menu continues to prompt until user chooses quit MENU option 7
    while notQuit:
        try:
            choice = user_selection()
            available_buckets = list_buckets_available()
            
            #MENU CHOICE 1 = CREATE BUCKET
            if choice == 1:
                firstname = input('Please enter your firstname: ').lower()
                lastname = input('Please enter your lastname: ').lower()
                digits = '1' #holder that doesn't validate
                #input validation to verify 6 digits 0-9 are only used
                while not re.match("^\d{6,6}$", digits):
                    print("Please make sure you typed a number of 6 digits 0-9")
                    digits=input('Choose 6 numbers, example: 123456: ')
                #if valid input creates bucket_name combination and attempts to create
                else:
                    bucket_name = firstname+lastname+'-'+digits
                    created = create_bucket(bucket_name)
                    if created:
                        logging.info(f'{bucket_name} was created')
                        available_buckets = list_buckets_available()
                        print('The new available buckets to choose from: \n' +available_buckets)
                        
            #MENU CHOICE 2 = PUT OBJECT INTO BUCKET   
            elif choice == 2:
                print('The available buckets to choose from: \n' +available_buckets)
                bucket_name = input('Please enter bucket name to put file into: ').lower()
                filename = input('Please enter file name to put into bucket: ')
                object_to_bucket = object_to_previous_bucket(bucket_name, filename)
                if object_to_bucket:
                    logging.info(f'{filename} was put into {bucket_name} bucket')
                if not object_to_bucket:
                    filename = input('Please enter file name to put into bucket: ')
                    object_to_bucket = object_to_previous_bucket(bucket_name, filename)
                objects = list_items_available(bucket_name)
                if objects is not None:
                    logging.info(f'Objects in {bucket_name}')
                    for obj in objects:
                        logging.info(f' {obj["Key"]}')
                        
            #MENU CHOICE 3 = DELETE AN OBJECT IN A BUCKET
            elif choice == 3:
                print('The available buckets to choose from: \n' +available_buckets)
                bucket_name = input('Please enter bucket name: ').lower()
                #Checks to verify bucket exists
                if bucket_exists(bucket_name):
                    logging.info(f'{bucket_name} exists and you have permission to access it.')
                    objects = list_items_available(bucket_name)
                    #if exists then check to see if items 
                    if objects is not None:
                        logging.info(f'Objects in {bucket_name}')
                        for obj in objects:
                            logging.info(f" {obj['Key']}")
                        object_name = input('Please enter file name delete: ')
                        deleted = delete_object(bucket_name, object_name)
                    #if item was found and successfully deleted
                    if deleted:
                        logging.info(f'{object_name} was deleted from {bucket_name}')
                #if bucket doesn't exist        
                else:
                    logging.info(f'{bucket_name} does not exist or '
                                 f'you do not have permission to access it.')
                
            #MENU OPTION 4 = DELETE A BUCKET
            elif choice == 4:
                print('The available buckets to choose from: \n' +available_buckets)
                bucket_name = input('What bucket would you like to delete?').lower()
                deleted = delete_bucket(bucket_name)
                #if bucket deleting returns true
                if deleted:
                    logging.info(f'{bucket_name} was deleted')
                    available_buckets = list_buckets_available()
                    print('The now available buckets to choose from: \n' +available_buckets)
                    
            #MENU OPTION 5 = COPY AN OBJECT FROM ONE BUCKET TO ANOTHER
            elif choice == 5:
                print('The available buckets to choose from: \n' +available_buckets)
                src_bucket_name = input('Please enter bucket name to copy from: ').lower()
                objects = list_items_available(src_bucket_name)
                #if objects are available
                if objects is not None:
                    logging.info(f'Objects in {src_bucket_name}')
                    for obj in objects:
                        logging.info(f" {obj['Key']}")
                    src_object_name = input('Please enter which file to copy from ' +src_bucket_name +' : ')
                    dest_bucket_name = input('Please enter which bucket to copy file to: ').lower()
                    dest_object_name = input('Please enter what you want the file to be named: ')
                    success = copy_object_to_bucket(src_bucket_name, src_object_name,
                             dest_bucket_name, dest_object_name)
                if success:
                    logging.info(f'Copied {src_bucket_name}/{src_object_name} to '
                                 f'{dest_bucket_name}/{dest_object_name}')
                                 
            #MENU OPTION 6 = DOWNLOAD OBJECT FROM BUCKET
            elif choice == 6:
                print('The available buckets to choose from: \n' +available_buckets)
                bucket_name = input('Which bucket would you like to download from?')
                objects = list_items_available(bucket_name)
                #if objects is available
                if objects is not None:
                    logging.info(f'Objects in {bucket_name}')
                    for obj in objects:
                        logging.info(f" {obj['Key']}")
                    key = input('Which file would you like to download?')
                    download_bucket(bucket_name, key)
            
            #MENU OPTION 7 = EXIT PROGRAM
            elif choice == 7:
                print('You have opted to quit:')
                print(time()) 
                quit()
            #IF USER DOESN'T ENTER VALID MENU OPTION 1-7
            else: 
                print("Invalid choice.  Enter 1-7")
                menu()
            
        #CATCHES ERROR IF ANYTHING BUT NUMBERS ARE USED
        except(ValueError):
                print('Please enter valid choice.')
                menu()
                
#PROGRAM MAIN
def main():
    print('******** Welcome to the S3 Bucket Application ********')
    menu()
    
#CALLING MAIN
main()