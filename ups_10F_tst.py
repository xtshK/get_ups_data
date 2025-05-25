import requests
from bs4 import BeautifulSoup
import os
import csv
import pandas as pd
from datetime import datetime, timedelta

def get_html_content(url, username, password, target_hour, target_mins, time_range):

    response = requests.get(url,auth=(username,password))
    soup = BeautifulSoup(response.content, 'html.parser')

    # columns = ["DateTime", "Vin", "Vout", "Freq", "Load", "Capacity", "BatteryVolt", "CellVolt", "Temp"] 10f default columns
    # Theothers floor columns.
    expected_headers = ['Date', 'Time', 'Vin', 'Vout', 'Vbat', 'Fin', 'Fout', 'Load', 'Temp']
    container = soup.find("div",id = "myTab1_Content0")
    
    # Find all tables in the page
    tables = container.find("tabel") if container else None

    if not tables:
        print("No data found in the specified table.")
        return None

    data = []

    for tabel in tables:
        first_row = tabel.find("tr")
        if not first_row:
            continue






if __name__ == "__main__":
    ups = "http://172.21.2.13/DataLog.cgi"

    username = "admin"
    password = "misadmin"

    # target time
    ups_target_hour = 13
    ups_target_mins = 30
    ups_time_range = 45

