from update_items import set_update_expressions, set_keys, set_expression_values, update_items

if __name__ == "__main__":

    
    # Get the attributes to update
    attributes_input = input("Please enter the attribute names to update (ie: opened, eventType,): ").strip()

    # Get the key values
    userId = input("Enter userId: ").strip()
    giftId = input("Enter giftId: ").strip()
    
    if not userId or not giftId:
        print("Both userId and giftId are required. Exiting.")
        exit()

    update_expressions = set_update_expressions(attributes_input)
    if not update_expressions:
        print("Failed to create update expressions. Exiting.")
        exit()

    expression_values = set_expression_values(attr_inputs=attributes_input, value=True)
    if not expression_values:
        print("Failed to create expression values. Exiting.")
        exit()
    
    # Set the composite primary key
    keys = set_keys(key_names=["userId", "giftId"], key_values=[userId, giftId])
    
    print(f"Update Expression: {update_expressions}")
    print(f"Expression Values: {expression_values}")
    print(f"Keys: {keys}")
    
    if keys:  # Only proceed if keys are properly set
        print(f"Table: bitruth-lambda-service-api-gifts")
        print(f"Key: {keys}")
        print(f"Attributes to update: {attributes_input}")
        
        try:
            update_items(
                table_name="bitruth-lambda-service-api-gifts",
                key=keys,
                update_expression=update_expressions,
                expression_values=expression_values
            )
        except Exception as e:
            print(f"Update failed: {e}")
    else:
        print("Failed to set keys properly")