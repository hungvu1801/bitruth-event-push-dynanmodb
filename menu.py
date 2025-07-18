import json


from insert_items import add_attribute_if_missing, create_gifts, create_multiple_gifts_via_API_call
from helper import get_json_from_url, parse_data, save_data_to_file, read_data_from_file, clear_console, get_file_dir, read_headers_from_file
from get_items import get_items

def print_menu() -> None:
    print("=" * 50)
    print("🎁 Gift Management Console 🎁".upper().center(50," "))
    print("=" * 50)
    print("1. Create Gifts from API Call")
    print("2. Create Gifts from CSV File")
    print("3. Fetch Items from DynamoDB 📦")
    print("4. Query Data via API 🔍")
    print("0. Exit the Program ")
    print("=" * 50)

def choose_option() -> int:
    while True:
        try:
            option = int(input("Choose an option: "))
            if option in [0, 1, 2, 3, 4]:
                return option
            else:
                print("Invalid option. Please choose again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def run_command(command: int) -> int:
    if command == 1:
        items_full = get_json_from_url()
        eventType = input("Enter eventType (ie: lucky-box-3 | lucky-box-2): ").strip()
        items_parse = parse_data(
            data=items_full,
            is_api=True)
        # print(items_full)
        # print(items_parse)
        print(f"Number of items in API call: {len(items_full)}")
        create_multiple_gifts_via_API_call(data=items_parse)
        return 1
    elif command == 2:
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
    elif command == 0:
        return 0
    elif command == 3:
        table_name = input("Please enter the table name:").strip()
        if not table_name:
            table_name = 'bitruth-lambda-service-api-gifts'
        attributes = {
            "eventType": "lucky-box-3"
        }
        get_items(table_name=table_name, attributes=attributes)
        return 1
    elif command == 4:
        items_full = get_json_from_url()
        print(json.dumps(items_full, indent=4))
        return 1
    else:
        return 0
    
def controller() -> None:
    while True:
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

