import requests
import json
from dotenv import load_dotenv
import os, sys
from datetime import datetime
from typing import Dict, Any, List, Tuple
import tkinter as tk
from tkinter.filedialog import askopenfilename

load_dotenv()

def get_file_dir() -> None:
    while True:
        try:
            root = tk.Tk()
            root.withdraw()
            file_name = askopenfilename(
                title="Select file", 
                filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")])
            if not file_name:
                print("No file selected. Please try again.")
                continue
            return file_name
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

def clear_console():
    if sys.platform.startswith('win'):
        os.system('cls')  # Command for Windows

def get_json_from_url() -> List[Dict[str, Any]]:
    
    url = os.getenv("HISTORY_URL")
    # Validate dates
    while True:
        start_date = input("Enter start date (YYYY-MM-DDTHH:MM:SS) ie: 2025-07-10T23:59:59 : ").strip()
        end_date = input("Enter start date (YYYY-MM-DDTHH:MM:SS) ie: 2025-07-10T23:59:59 : ").strip()
        if not start_date or not end_date:
            raise ValueError("Start date and end date must be provided.")
        try:
            datetime.fromisoformat(start_date)
            datetime.fromisoformat(end_date)
            break
        except ValueError:
            raise ValueError("Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS).")
    params = {
        "startDate": start_date,
        "endDate": end_date,
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('USER_BEARER')}",
        "Content-Type": "application/json"
    }

    reponse = requests.get(
        url,
        headers=headers,
        params=params)
    if reponse.status_code != 200:
        raise Exception(f"Failed to fetch data: {reponse.status_code} - {reponse.text}")
    try:
        data = reponse.json()
    except json.JSONDecodeError:
        raise ValueError("Response is not valid JSON")
    items = data.get("data").get("items", [])
    if not items:
        return []
    return items


def parse_data(
        data: List[Dict[str, Any]],
        is_api: bool = True,
        eventType: str = "lucky-box-2",
        headUID: str = None, 
        headGiftBox: str = None,
        giftType: str = "EXTERNAL_GIFT") -> List[Dict[str, Any]]:
    """
    Parse data from the JSON response.
    [{
        "userId": "806",
        "giftBoxNumber": 10,
        "giftType": "DAILY_CHECKIN",
        "eventType": "lucky-box-2"
    }, {} ... ]
    """
    parsed_data = []

    for item in data:
        try:
            if not is_api: # If data not from API
                userId = str(item.get(headUID)) # This is for file input
                giftBoxNumber = int(item.get(headGiftBox))
            else:
                userId = str(item.get("rootUserId")) # This is for API input
                giftType = item.get("type", "EXTERNAL_GIFT").upper()  # Default to EXTERNAL_GIFT if not provided
                if userId == '968':
                    print(giftType)
                # input()
                giftBoxNumber = int(item.get("luckyBoxReceived"))
            if not eventType:
                eventType = "lucky-box-2" # Fallback
            parsed_item = {
                "userId": userId,
                "giftBoxNumber": giftBoxNumber,
                "giftType": giftType,
                "eventType": eventType,  # Default value
            }
            parsed_data.append(parsed_item)
        except (ValueError, TypeError) as e:
            print(f"Error parsing item {item}: {e}")
    return parsed_data

def save_data_to_file(data: Dict[str, Any], filename: str, type: str) -> None:
    if type == "json":
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
    elif type == "csv":
        import pandas as pd
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)

def read_data_from_file(filename: str) -> List[Dict[str, Any]]:
    type = os.path.splitext(filename)[1][1:]  # Get file extension
    if type == "json":
        with open(filename, 'r') as file:
            return json.load(file)
    elif type == "csv":
        import pandas as pd
        df = pd.read_csv(filename)
        return df.to_dict(orient='records')
    else:
        raise ValueError("Unsupported file type. Use 'json' or 'csv'.")

def read_headers_from_file(filename: str) -> Tuple[str, str]:
    type = os.path.splitext(filename)[1][1:]
    if type =="json":
        with open(filename, 'r') as file:
            data = json.load(file)
            if isinstance(data, dict):
                headers = list(data.keys())
                return (headers[0], headers[1])
    elif type == "csv":
        import pandas as pd
        df = pd.read_csv(filename)
        return (df.columns[0], df.columns[1])  # Assuming first two columns are userId and giftBoxNumber
    else:
        raise ValueError("Unsupported file type. Use 'json' or 'csv'.")
    
def get_input_from_user() -> dict:
    result_input = dict()
    while True:
        try:
            result_input["userId"] = input("Enter userId (ie: 806): ").strip()
            result_input["eventType"] = input("Enter eventType (ie: lucky-box-2 | lucky-box-1): ").strip()
            result_input["IndexName"] = input("Enter IndexName (ie: ): ").strip()
            result_input["rewardType"] = input("Enter rewardType (ie:): ").strip()
            result_input["claimed"] = input("Enter claimed (ie: True | False): ").strip()
            return result_input
        except Exception as e:
            print(f"Invalid input: {e}")
            continue