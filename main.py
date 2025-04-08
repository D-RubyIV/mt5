import MetaTrader5 as mt5
from datetime import datetime

import pandas as pd

mt5.initialize()
login = 244519321
password = "Ha19102004dzz@#"
server = "Exness-MT5Trial14"
authorized = mt5.login(login=login, password=password, server=server)
print("Login result:", authorized)
symbols = mt5.symbols_get()

symbol = "XAUUSDm"
timeframe = mt5.TIMEFRAME_H1
date_from = datetime(2025, 4, 7)
date_to = datetime.now()
prices = pd.DataFrame(
    mt5.copy_rates_range(
        symbol,
        timeframe,
        date_from,
        date_to
    )
)
prices["time"] = pd.to_datetime(prices["time"], unit="s")
print(prices)
