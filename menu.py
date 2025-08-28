import json


from insert_items import add_attribute_if_missing, create_gifts, create_multiple_gifts_via_API_call
from helper import get_json_from_url, parse_data, save_data_to_file, read_data_from_file, clear_console, get_file_dir, read_headers_from_file
from get_items import scan_items
from update_items import set_update_expressions, set_keys, set_expression_values, update_items

def print_menu() -> None:
    print("=" * 50)
    print("🎁 Gift Management Console 🎁".upper().center(50," "))
    print("=" * 50)
    print("1. Create Gifts from API Call")
    print("2. Create Gifts from CSV File")
    print("3. Scan and Filter Items from DynamoDB 📦")
    print("4. Scan and Update Items from DynamoDB 🔍")
    print("5. Query Data via API 🔍")
    print("0. Exit the Program ")
    print("=" * 50)

def choose_option() -> int:
    while True:
        try:
            option = int(input("Choose an option: "))
            if option in [0, 1, 2, 3, 4, 5]:
                return option
            else:
                print("Invalid option. Please choose again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            break

def run_command(command: int) -> int:

    if (command == 1):
        items_full = get_json_from_url()
        eventType = input("Enter eventType (ie: lucky-box-3 | lucky-box-2): ").strip()
        items_parse = parse_data(
            data=items_full,
            is_api=True)
        print(f"Number of items in API call: {len(items_full)}")
        create_multiple_gifts_via_API_call(data=items_parse)
        return 1
    
    elif (command == 2):
        file_name = get_file_dir()
        if not file_name:
            print("No file selected. Please try again.")
            return 0
        items_full = read_data_from_file(filename=file_name)
        headers = read_headers_from_file(filename=file_name)
        eventType = input("Enter eventType (ie: lucky-box-3 | lucky-box-2): ").strip()
        giftType = input("Enter giftType (ie: DAILY_CHECKIN | LEADER_BOARD): ").strip()
        
        items_parse = parse_data(
            data=items_full,
            is_api=False,
            eventType=eventType,
            giftType=giftType,
            headUID=headers[0], 
            headGiftBox=headers[1])
        create_multiple_gifts_via_API_call(data=items_parse)
        return 1
    
    elif (command == 0):
        return 0
    
    elif (command == 3 or command == 4):
        table_name = input("Please enter the table name (ie: bitruth-lambda-service-api-gifts): ").lower().strip()
        eventType = input("Enter eventType (ie: lucky-box-3 | lucky-box-2): ").lower().strip()
        
        # Validate opened input
        while True:
            opened = input("Enter opened (ie: true | false): ").lower().strip()
            if opened in ['true', 'false']:
                break
            else:
                print("Invalid input. Please enter 'true' or 'false'.")
                continue
        
        while True:
            try:
                limit_input = input("Enter limit (ie: 10): ").strip()
                if not limit_input:  # Handle empty input
                    limit = None
                else:
                    limit = int(limit_input)
                    if limit <= 0:  # Handle zero or negative input
                        limit = None
                break
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

        items = scan_items(
            table_name=table_name,
            event_type=eventType,
            opened=opened,
            limit=limit
        )

        print(json.dumps(items, indent=4))
        print(len(items))
        if command == 4:
            if len(items) == 0:
                print("No items to update.")
                return 1
            attributes_input = input("Please enter the attribute names to update (ie: opened, eventType,): ")
            update_expressions = set_update_expressions(attributes_input)
            expression_values = set_expression_values(attr_inputs=attributes_input, value=True)
            print(update_expressions)
            print(expression_values)
            # Loop through items to update each
            for item in items:
                # if item["userId"] == "806":
                try:
                    keys = set_keys(
                        key_names=["userId", "giftId"], 
                        key_values=[item["userId"], item["giftId"]])
                    
                    print(keys)
                    update_items(
                        table_name=table_name,
                        key=keys,
                        update_expression=update_expressions,
                        expression_values=expression_values
                    )
                    print(f"Update {item['userId']} - {item['giftId']} completed.")
                except Exception as e:
                    print(f"Update failed: {e}")

        return 1
    elif command == 5:
        items_full = get_json_from_url()
        print(json.dumps(items_full, indent=4))
        return 1
    else:
        return 0
    
def controller() -> None:
    while True:
        try:
            clear_console()
            print_menu()
            command = choose_option()
            if command == 0:
                print("Exiting...")
                break
            result = run_command(command)
            if result == 0:
                print("An error occurred. Please try again.")
            else:
                print("Command executed successfully.")
            input("Press Enter to continue...")
            clear_console()
        except KeyboardInterrupt:
            print("KeyboardInterrupt Detected .. Exit program ..")
            return

