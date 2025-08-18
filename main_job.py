from datetime import datetime
from insert_items import create_multiple_gifts_via_API_call
from helper import get_json_from_url, parse_data
from notification import send_notification_discord
from helper import convert_time_to_str

if __name__ == "__main__":
    try:
        items_full = get_json_from_url(is_date_input=False)

        items_parse = parse_data(
            data=items_full,
            is_api=True)

        result = create_multiple_gifts_via_API_call(data=items_parse)
        send_notification_discord(message=f"""[LUCK BOX JOB]: Job Runs Successful At {convert_time_to_str(datetime.now())}. \nTotal users success: {result["success"]}, failed: {result["fail"]}.""")
    except Exception as e:
        print(e)
        send_notification_discord(message=f"[LUCK BOX JOB]: Job Fail At {convert_time_to_str(datetime.now())}: {e}")
