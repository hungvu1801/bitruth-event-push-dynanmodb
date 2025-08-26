import json
import requests
from typing import List, Dict, Any, Optional
from assets import BINANCE_FEE_URL, HEADERS

def get_coins_from_Binance() -> Optional[List[Dict[str, Any]]]:
    try:
        response = requests.get(url=BINANCE_FEE_URL, headers=HEADERS)
        if response.status_code != 200 or response.status_code != 201:
            return None
        data = json.loads(response.content.decode('utf-8', errors='ignore'))
        coins = data["data"]
        return coins
    except Exception as e:
        return None


def main():
    ...