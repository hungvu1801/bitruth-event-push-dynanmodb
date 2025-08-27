SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = "13qPYXpfsqWf5ElQDklDejr88U6m0BXFUVyjEpDjg3bg" # set up this for write to appointed sheet

SHEET_NAME = ""

# Setting this to filter coins in BITRUTH_COINS
# if IS_GET_ALL = 0 we will get ALL coins from Binance
# if IS_GET_ALL = 1 we will filter by BITRUTH_COINS
IS_GET_ALL = 1 # 0 : False, 1 : True  

BITRUTH_COINS = [
    "LTC", "SOL", "XRP", 
    "BNB", "ADA", "BCH", 
    "BTC", "ETH", "TRX", 
    "LINK", "SUI", "AVAX", 
    "XLM", "TON", "SHIB", 
    "PEPE", "TRUMP", "RENDER", 
    "ONDO", "HBAR"]