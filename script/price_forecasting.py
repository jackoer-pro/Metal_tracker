
# %%
import requests
import datetime

end   = datetime.datetime.now()
start = end - datetime.timedelta(days=30)

url = "https://metal-sentinel.p.rapidapi.com/metal-history"

querystring = {
    "symbol"   : "AG",
    "currency" : "USD",
    "startTime": str(int(start.timestamp())),
    "endTime"  : str(int(end.timestamp())),
    "limit"    : "30",
    "offset"   : "1"
}

headers = {
    "x-rapidapi-key" : "0003b83ac5msh1e0fec7f533c1bcp194924jsnb293ea24fbc9",
    "x-rapidapi-host": "metal-sentinel.p.rapidapi.com",
    "Content-Type"   : "application/json"
}

response = requests.get(url, headers=headers, params=querystring)
print(response.status_code)
print(response.json())
# %%
