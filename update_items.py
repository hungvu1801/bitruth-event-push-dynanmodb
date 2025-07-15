from init_table import init_table

def update_tbl_dydb(
        table_name: str, 
        key: str, 
        update_expression: str, 
        expression_values: str) -> None:
    """
    Update item in DynamoDB
        table_name: str, name of the DynamoDB table
        key: dict, primary key of the item to update
        update_expression: str, update expression (e.g., "SET attr1 = :val1")
        expression_values: dict, values used in the update expression (e.g., {":val1": "new value"})
    :return: dict, response from DynamoDB

    """

    table = init_table(table_name=table_name)
    if not table:
        return
    try:
        response = table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
        print("Updated Successfully")
    except Exception as e:
        print(f"Error {e}")
