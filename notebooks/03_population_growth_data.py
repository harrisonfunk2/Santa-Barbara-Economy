import requests
import pandas as pd

API_KEY = "YOUR_CENSUS_API_KEY"
YEAR = "2022"
STATE = "06"
COUNTY = "083"

url = f"https://api.census.gov/data/{YEAR}/acs/acs5?get=B01003_001E&for=county:{COUNTY}&in=state:{STATE}&key={API_KEY}"

response = requests.get(url)
data = response.json()

df = pd.DataFrame(data[1:], columns=data[0])
df.columns = ['population', 'state', 'county']
df['year'] = YEAR
df.to_csv("data/population.csv", index=False)
df.head()