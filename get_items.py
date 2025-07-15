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

def get_items(table_name: str, **attributes: dict) -> list:
    """
    Get items from DynamoDB table based on attributes.
    """
    try:
        table = init_table(table_name=table_name)
        query_kwargs = dict() # store query parameters
        key_condition_exp_lst = list() # store KeyConditionExpression
        filter_exp_lst = list() #store FilterExpression
        items_get_lst = list() # store items to return
        if not table:
            print("Init table failed.")
            return
        
        if attributes.get("userId"):
            key_condition_exp_lst.append(Attr("userId").eq(attributes.get("userId")))
        if attributes.get("eventType"):
            key_condition_exp_lst.append(Attr("eventType").eq(attributes.get("eventType")))
        if attributes.get("index_name"):
            query_kwargs["IndexName"] = attributes.get("index_name")
        if attributes.get("rewardType"):
            filter_exp_lst.append(Attr("rewardType").eq(attributes.get("rewardType")))
        if attributes.get("claimed"):
            filter_exp_lst.append(Attr("claimed").eq(attributes.get("claimed")))
        if filter_exp_lst:
            filter_exp = filter_exp_lst[0]
            for exp in filter_exp_lst[1:]:
                filter_exp &= exp
        if key_condition_exp_lst:
            key_cond_exp = key_condition_exp_lst[0]
            for key in key_condition_exp_lst[1:]:
                key_cond_exp &= key

        if filter_exp_lst:
            query_kwargs["FilterExpression"] = filter_exp 

        if key_condition_exp_lst:
            query_kwargs["KeyConditionExpression"] = key_cond_exp
        
        while True:
            response = table.query(**query_kwargs)
            items = response.get("Items", [])
            items_get_lst.extend(items)
            if not items:
                break
            
            if "LastEvalueatedKey" not in response:
                break
            query_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
        return items_get_lst
    except ClientError as e:
        print(f"Error fetching items: {e.response['Error']['Message']}")
        return []
    
