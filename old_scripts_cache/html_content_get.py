import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# test session with a GET request to the URL
base_url = "http://172.21.2.13"
datalog_url = f"{base_url}/DataLog.cgi"
refresh_url = f"{base_url}/refresh_data.cgi"

password = "misadmin"
username = "admin"

session = requests.Session()
session.auth = (username, password)

session.get(refresh_url,params={"data_date": "20250601"})

response = session.get(datalog_url)
soup = BeautifulSoup(response.content, 'html.parser')

print(soup.prettify())

'''
tables = soup.find_all('table')
if not tables:
    print("No tables found in the HTML content.")
else:
    print(f"Found {len(tables)} tables in the HTML content.")
    for table in tables:
        print(table.prettify())
'''