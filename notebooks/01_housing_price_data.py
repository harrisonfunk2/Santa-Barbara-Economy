from fredapi import Fred
import pandas as pd

FRED_API_KEY = "YOUR_FRED_API_KEY"
fred = Fred(api_key=FRED_API_KEY)

series_id = "ATNHPIUS06083A"

data = fred.get_series(series_id)

df = data.reset_index()
df.columns = ['date', 'housing_price_index']
df.to_csv("data/housing_prices.csv", index=False)

df.head()
