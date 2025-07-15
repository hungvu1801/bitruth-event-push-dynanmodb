from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
import os
import pandas as pd
import json
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
from typing import List
import time

from GiftRecord import GiftRecord
from init_table import init_table

load_dotenv()

API_CREATE_GIFTS = os.getenv('API_CREATE_GIFTS')
username = os.getenv('USERNAME_BT')
password = os.getenv('PASSWORD_BT')

def add_attribute_if_missing(table_name, attribute_name: str, update_val: str) -> None:
    """
    Add attribute if missing
    """
    table = init_table(table_name=table_name)
    if not table:
        print("Init table failed.")
        return
    
    key_schema = table.key_schema
    key_attributes = [key['AttributeName'] for key in key_schema] # Get key attribute in table schema

    scan_kwargs = {
        "FilterExpression": Attr(attribute_name).not_exists()
    }
    while True:
        response = table.scan(**scan_kwargs)

        items = response.get("Items", [])

        if not items:
            break
        print(f"Found {len(items)} items missing 'eventType'.")
        for item in items:
            key = {attr: item[attr] for attr in key_attributes if attr in item}
            try:
                table.update_item(
                    Key=key,
                    UpdateExpression="SET #attr = :val",
                    ExpressionAttributeNames={"#attr": attribute_name},
                    ExpressionAttributeValues={":val": update_val},
                    ConditionExpression="attribute_not_exists(#attr)"
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    print(f"Skipped: eventType already exists for {key}")
                else:
                    print(f"Failed to update {key}: {e.response['Error']['Message']}")
        if "LastEvalueatedKey" not in response:
            break
        scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

def save_multiple_gifts(table, gifts: List[GiftRecord]) -> bool:
    try:
        with table.batch_writer() as batch:
            for gift in gifts:
                batch.put_item(Item=gift.to_dynamodb_item())
        return True
    except Exception as e:
        print(f"Fail batch insertion {e}")
        return False


def create_gifts(file_name: str) -> list[GiftRecord]:
    print("-----------------------------------------")
    event_type = input("Please enter event type (e.g., lucky-box-1 | lucky-box-1): ").strip()
    try:
        df = pd.read_csv(file_name, header=0)
    except FileNotFoundError:
        print(f"Error: File {file_name} not found")
        return []
    except pd.errors.EmptyDataError:
        print(f"Error: File {file_name} is empty")
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []
    
    gifts = []
    data_records = [tuple(row) for row in df.to_records(index=False)]
    failed_users = 0
    success_users = 0
    failed_users_lst = []
    for record in data_records:
        try:
            user_id = str(record[0]) # record[0] is user_id
            num_boxes = int(record[2]) # record(2) is number of boxes
            if num_boxes <= 0:
                print(f"Warning: User {user_id} has {num_boxes} boxes, skipping")
                continue
            for _ in range(int(num_boxes)): 
                gift = GiftRecord(
                    user_id=user_id,
                    description="Gift boxes from game",
                    event_type=event_type,
                    gift_type="EXTERNAL_GIFT",
                )
                print(gift)
                gifts.append(gift)
            success_users += 1
        except (ValueError, IndexError) as e:
            failed_users += 1
            user_id = record[0] if len(record) > 0 else "unknown"
            failed_users_lst.append(user_id)
            print(f"Error processing user {user_id}: Invalid data format - {e}")
        except Exception as e:
            print(f"Error in record {record[0]}.")

    print(f"Processed {len(data_records)} records: {success_users} successful, {failed_users} failed.")
    print(f"Failed users: {failed_users_lst}")
    return gifts

def create_multiple_gifts_via_API_call(data: list) -> bool:
    for item in data:
        response = create_one_gift_via_API_call(json_data=item)
        if response.status_code != 200 and response.status_code != 201:
            print(f"Failed to create gift for user {item['userId']}: {response.text if response else 'No response'}")
        else:
            print(f"Successfully created gift for user {item['userId']}")

def create_one_gift_via_API_call(json_data: dict):
    try:
        # Set up headers
        headers = {
            'Content-Type': 'application/json' if json_data else 'application/x-www-form-urlencoded',
            'User-Agent': 'Python-requests/2.31.0'
        }
        
        # Make the POST request with basic authentication
        response = requests.post(
            url=API_CREATE_GIFTS,
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            json=json_data,
            timeout=30
        )
        time.sleep(1)  # Sleep for 1 second to avoid rate limiting
        # Print response content
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                print(f"Response JSON: {response.json()}")
            except json.JSONDecodeError:
                print(f"Response Text: {response.text}")
        else:
            print(f"Response Text: {response.text}")
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None