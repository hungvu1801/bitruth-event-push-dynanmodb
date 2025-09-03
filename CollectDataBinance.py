from curl_cffi import requests as curl_requests
from datetime import datetime
from dataclasses import dataclass, fields
import json
import requests
from typing import List, Dict, Any, Optional, Generator
import time

from assets import BINANCE_FEE_URL, HEADERS_BINANCE, BITRUTH_FEE_URL, HEADERS_BITRUTH
from GoogleSheet import GSheetWrite, GSheetService
from settings import BITRUTH_COINS, SPREADSHEET_ID, IS_GET_ALL

@dataclass
class CoinBase:
    coin_symbol: str = None
    coin_name: str = None
    network_short: str = None
    network_full: str = None
    minimum_deposit: str = None
    minimum_withdrawal: str = None
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
            response = requests.get(url=BINANCE_FEE_URL, headers=HEADERS_BINANCE)
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

    def write_records_into_sheet(
            self, coins_generator: Generator[Dict[str, Any], None, None], 
            coins_bitruth: list):
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
                time.sleep(4)  # Let's wait for data to write properly
                last_row = 1  # Headers are in row 1, so next data starts at row 2 (index 1)
            
            while True:
                coin = next(coins_generator)
                coin_base = CoinBase()
                time.sleep(1)
                coin_base.coin_symbol = coin["coin"]
                coin_base.coin_name = coin["name"]
                
                for network in coin["networkList"]:
                    try:
                        coin_base.network_short = network.get("network", "").strip()
                        coin_base.network_full = network.get("name", "").strip()
                        coin_base.minimum_deposit = (network.get("depositDust") or "").strip()
                        coin_base.minimum_withdrawal = network.get("withdrawMin", "").strip()
                        coin_base.deposit_fee = network.get("depositFee", "").strip()
                        coin_base.withdrawal_fee = network.get("withdrawFee", "").strip()
                        coin_base.denomination = network.get("denomination", "").strip()
                        
                        for coin_bitruth in coins_bitruth:
                            if (coin_base.coin_symbol == coin_bitruth.coin_symbol and coin_base.network_short == coin_bitruth.network_short):
                                if (coin_base.minimum_deposit != coin_bitruth.minimum_deposit or 
                                    coin_base.minimum_withdrawal != coin_bitruth.minimum_withdrawal or
                                    coin_base.deposit_fee != coin_bitruth.deposit_fee or
                                    coin_base.withdrawal_fee != coin_bitruth.withdrawal_fee):

                                    next_empty_row = last_row + 1
                                    range_name = f"{self.title}!A{next_empty_row}"
                                    data = [coin_base.get_datas()]
                                    self.gwrite.write_to_gsheet(data=data, range_name=range_name)
                                    last_row = next_empty_row
                    except Exception as e:
                        print(f"Error in write_records_into_sheet: {e}")
                        print(network)
                        continue
        except StopIteration:
            return  # Generator exhausted
        except Exception as e:
            print(f"Error in write_records_into_sheet: {e}")
    
    def main_execution(self) -> None:
        # get coins bitruth
        collect_bitruth = CollectDataBitruth()
        coins_bitruth = collect_bitruth.get_coins_from_Bitruth()
        if not coins_bitruth:
            print("Failed to fetch coins from Bitruth")
            return
            
        collect_bitruth.filter_and_clean_coins(coins_bitruth)

        # get coins binance
        if not self.gwrite or not self.gwrite.create_new_sheet(title=self.title):
            print("Failed to create new sheet or gwrite is None")
            return
        
        coins_binance = CollectDataBinance.get_coins_from_Binance()
        if not coins_binance:
            print("Failed to fetch coins from Binance")
            return

        coins_generator = CollectDataBinance.filter_coins(coins_binance)

        self.write_records_into_sheet(coins_generator, collect_bitruth.coins)

class CollectDataBitruth:
    def __init__(self):
        self.coins = []

    def get_coins_from_Bitruth(self) -> Optional[List[Dict[str, Any]]]:
        try:
            coins_lst = []
            url = BITRUTH_FEE_URL
            while True:
                response = curl_requests.get(url=url, impersonate="chrome")
                if response.status_code != 200 and response.status_code != 201:
                    return None
                data = json.loads(response.content.decode('utf-8', errors='ignore'))
                coins_lst.extend(data["data"]["data"])
                url = data["data"]["next_page_url"]
                if not url:
                    break
            return coins_lst
        except Exception as e:
            print(f"Error: {e}")
            return None

    def filter_and_clean_coins(self, coins_lst: List[Dict[str, Any]]) -> None:

        for item in coins_lst:
            for network in item["networks"]:
                coin = CoinBase()
                coin.coin_symbol = item["key"].upper()
                coin.network_short = network.get("name", "")
                coin.deposit_fee = "0" if network.get("depositFee", "").lower().strip() == "free" else network.get("depositFee", "")
                coin.minimum_deposit = network.get("minDeposit", "")
                coin.minimum_withdrawal = network.get("minWithdrawal", "")
                coin.withdrawal_fee = network.get("withdrawalFee", "")
                
                self.coins.append(coin)