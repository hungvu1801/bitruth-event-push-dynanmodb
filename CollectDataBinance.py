from datetime import datetime
from dataclasses import dataclass, fields, asdict
import json
import requests
from typing import List, Dict, Any, Optional, Generator
import time

from assets import BINANCE_FEE_URL, HEADERS
from GoogleSheet import GSheetWrite, GSheetService
from settings import BITRUTH_COINS, SPREADSHEET_ID, IS_GET_ALL

@dataclass
class CoinBase:
    coin_symbol: str = None
    coin_name: str = None
    network_short: str = None
    network_full: str = None
    minimum_deposit: str = None
    minimum_withdrawal: str	= None
    deposit_fee: str = None
    withdrawal_fee: str = None
    denomination: str = None

    @classmethod
    def get_field_names(cls) -> List[str]:
        return [f.name for f in fields(cls)]

    def get_datas(self):
        return [getattr(self, f) for f in CoinBase.get_field_names()]

class CollectDataBinance:
    def __init__(self):
        self.gwrite = self.init_gsheetservice()
        self.title = datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def get_coins_from_Binance() -> Optional[List[Dict[str, Any]]]:
        try:
            response = requests.get(url=BINANCE_FEE_URL, headers=HEADERS)
            if response.status_code != 200 and response.status_code != 201:
                return None
            data = json.loads(response.content.decode('utf-8', errors='ignore'))
            coins = data["data"]
            return coins
        except Exception as e:
            return None

    @staticmethod
    def filter_coins(coins: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
        if IS_GET_ALL:
            for coin in coins:
                if coin["coin"].upper() in BITRUTH_COINS:
                    yield coin
        else:
            for coin in coins:
                    yield coin
    
    def init_gsheetservice(self) -> Optional[GSheetWrite]:
        gservice = GSheetService()
        if gservice.service == None:
            return None
        gwrite = GSheetWrite(gservice=gservice, spreadSheetId=SPREADSHEET_ID)
        return gwrite

    def write_records_into_sheet(self, coins_generator):
        try:
            range_name = f"{self.title}!A:A"
            print(range_name)
            last_row = self.gwrite.gservice.check_last_value_in_column(self.gwrite.spreadSheetId, range_name)
            print(f"last_row = {last_row}")
            
            # Write the header if needed
            if last_row == -1:
                data = [CoinBase.get_field_names()]
                header_range = f"{self.title}!A1"
                self.gwrite.write_to_gsheet(data=data, range_name=header_range)
                time.sleep(5)  # Let's wait for data to write properly
                last_row = 1  # Headers are in row 1, so next data starts at row 2 (index 1)
            
            while True:
                coin = next(coins_generator)
                coin_base = CoinBase()
                time.sleep(1)
                coin_base.coin_symbol = coin["coin"]
                coin_base.coin_name = coin["name"]
                
                for network in coin["networkList"]:
                    coin_base.network_short = network.get("network", "")
                    coin_base.network_full = network.get("name", "")
                    coin_base.minimum_deposit = network.get("depositDust", "")
                    coin_base.minimum_withdrawal = network.get("withdrawMin", "")
                    coin_base.deposit_fee = network.get("depositFee", "")
                    coin_base.withdrawal_fee = network.get("withdrawFee", "")
                    coin_base.denomination = network.get("denomination", "")
                    
                    next_empty_row = last_row + 1
                    range_name = f"{self.title}!A{next_empty_row}"
                    data = [coin_base.get_datas()]
                    self.gwrite.write_to_gsheet(data=data, range_name=range_name)
                    last_row = next_empty_row
        except StopIteration:
            return  # Generator exhausted
        except Exception as e:
            print(f"Error in write_records_into_sheet: {e}")
    
    def main_execution(self) -> None:
        if not self.gwrite or not self.gwrite.create_new_sheet(title=self.title):
            print("Failed to create new sheet or gwrite is None")
            return
        
        coins = CollectDataBinance.get_coins_from_Binance()
        if not coins:
            print("Failed to fetch coins from Binance")
            return

        coins_generator = CollectDataBinance.filter_coins(coins)
        
        self.write_records_into_sheet(coins_generator)