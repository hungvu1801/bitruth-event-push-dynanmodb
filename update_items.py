from botocore.exceptions import ClientError
from init_table import init_table
from typing import Dict, Any, Optional, Union
from assets import DYNAMODB_RESERVED_KEYWORDS

def update_tbl_dydb(
        table_name: str, 
        key: Dict[str, Any], 
        update_expression: str, 
        expression_values: Dict[str, Any],
        expression_names: Optional[Dict[str, str]]) -> Optional[Dict[str, Any]]:
    """
    Update item in DynamoDB
    Args:
        table_name: Name of the DynamoDB table
        key: Primary key of the item to update (e.g., {"id": "123"})
        update_expression: Update expression (e.g., "SET attr1 = :val1")
        expression_values: Values used in the update expression (e.g., {":val1": "new value"})
        expression_names: Optional attribute name mappings (e.g., {"#attr": "attribute"})
    
    Returns:
        Dict containing the response from DynamoDB, or None if failed
    
    Raises:
        ClientError: If DynamoDB operation fails
    """

    table = init_table(table_name=table_name)
    if not table:
        return
    update_params = {
        "Key": key,
        "UpdateExpression": update_expression,
        "ExpressionAttributeValues": expression_values,
        "ReturnValues": "UPDATED_NEW"
    }
    if expression_names:
        update_params["ExpressionAttributeNames"] = expression_names
    try:
        response = table.update_item(**update_params)
        print("Updated Successfully")
        return response
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"DynamoDB Error [{error_code}]: {error_message}") 
        raise
    except Exception as e:
        print(f"Error {e}")

def is_dynamodb_reserved_keywords(attrs_name: str) -> bool:
    return attrs_name.upper() in DYNAMODB_RESERVED_KEYWORDS

def set_update_expressions() -> Optional[str]:
    try:
        update_expression = "SET "
        attributes_input = input("Please enter the attribute names to update (ie: ): ")
        attributes_names = attributes_input.split(" ")

        if not attributes_names:
            print("No attributes provided for update.")
            return
        is_reserved_names = [is_dynamodb_reserved_keywords(attr) for attr in attributes_names]

        if is_reserved_names[0]:
            update_expression += f"#{attributes_names[0]} = :{attributes_names[0]}"
        else:
            update_expression += f"{attributes_names[0]} = :{attributes_names[0]}"

        for attr, is_reseverd in zip(attributes_names[1:], is_reserved_names[1:]):
            if is_reseverd:
                update_expression += f", #{attr} = :{attr}"
            else:
                update_expression += f", {attr} = :{attr}"

        return update_expression
    except Exception as e:
        print(f"Error in setting update expressions: {e}")
        return

def set_keys(
        user_input: bool=False, 
        key_names: Union[str, list]=None, 
        key_values: Union[str, list]=None) -> Optional[Dict[str, Any]]:
    try:
        key = {}
        if not user_input:
            if isinstance(key_names, str) and isinstance(key_names, str):
                key[key_names] = key_values
                return key
            elif isinstance(key_names, list) and isinstance(key_names, list):
                if len(key_names) != len(key_values):
                    return
            else:
                print("Invalid key names or values provided.")
                return
        else:
            key_input_ls = input("Please enter the key (Key Attributes) names to update (ie: ): ")
            key_values_ls = input("Please enter the key values (ie: ): ")
            key_names = key_input_ls.split(" ")
            key_values = key_values_ls.split(" ")

            if len(key_names) != len(key_values):
                print("Key names and values not matching.")
                return
            
        for name, value in zip(key_names, key_values):
            key[name] = value
        return key
    except Exception as e:
        print(f"Error in setting keys: {e}")
        return