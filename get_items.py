from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError
from typing import List, Optional


from GiftRecord import GiftRecord
from init_table import init_table



def get_items(table_name: str, **attributes) -> Optional[list]:
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
        # Use index if specified
        index_name = attributes.get("index_name")

        if attributes.get("userId"):
            key_condition_exp_lst.append(Key("userId").eq(attributes.get("userId")))
        if attributes.get("eventType"):
            key_condition_exp_lst.append(Key("eventType").eq(attributes.get("eventType")))
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
            
            if "LastEvaluatedKey" not in response:
                break
            query_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
        return items_get_lst
    except ClientError as e:
        print(f"Error fetching items: {e.response['Error']['Message']}")
        return None

def get_items_v2(
        table_name: str, 
        event_type: str, 
        status: str, 
        # index_name: str, 
        limit: int = 1, 
        scan_index_forward: bool = True) -> Optional[list]:
    try:
        items_get_lst = []
        table = init_table(table_name=table_name)
        query_kwargs = {
            "KeyConditionExpression": "eventType = :eventType",
            "FilterExpression": "#status = :status",
            "ExpressionAttributeNames": {
                "#status": "status"
            },
            "ExpressionAttributeValues": {
                ":eventType": event_type,
                ":status": status
            },
            "ScanIndexForward": scan_index_forward,
            "Limit": limit
        }
        # if index_name:
        #     query_kwargs["IndexName"] = index_name
        while True:
            
            response = table.query(**query_kwargs)
            
            items = response.get("Items", [])
            if not items:
                break
            items_get_lst.extend(items)
            if "LastEvaluatedKey" not in response:
                break
            query_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

        return items_get_lst
    except ClientError as e:
        print(f"Error fetching items: {e.response['Error']['Message']}")
        return None
    
def scan_items(
        table_name: str, 
        event_type: str, 
        opened: str, 
        limit: Optional[int]) -> Optional[list]:
    
    try:
        items_get_lst = []
        table = init_table(table_name=table_name)
        
        if not table:
            print("Failed to initialize table.")
            return None
        
        # Convert string input to proper boolean for DynamoDB comparison
        # Since DynamoDB stores opened as boolean, we need to convert string input to boolean
        opened_bool = opened.lower() == 'true'
        
        scan_kwargs = {
            "FilterExpression": Attr("eventType").eq(event_type) & Attr("opened").eq(opened_bool),
        }
        if limit and limit > 0:
            scan_kwargs["Limit"] = limit
            
        print(f"Scanning table '{table_name}' for eventType='{event_type}' and opened={opened_bool}")
        if limit:
            print(f"Limit set to: {limit}")
        
        while True:
            
            response = table.scan(**scan_kwargs)
            
            items = response.get("Items", [])
            if not items:
                break
            items_get_lst.extend(items)
            if "LastEvaluatedKey" not in response:
                break
            scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

        print(f"Found {len(items_get_lst)} items matching the criteria.")
        return items_get_lst
    except ClientError as e:
        print(f"Error fetching items: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None