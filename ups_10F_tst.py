import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def get_html_content(url, username, password, target_date):
    response = requests.get(url, auth=(username, password))
    soup = BeautifulSoup(response.content, 'html.parser')

    expected_headers = ['Date', 'Time', 'Vin', 'Vout', 'Vbat', 'Fin', 'Fout', 'Load', 'Temp']
    container = soup.find("div", id="myTab1_Content0")
    target_table = container.find("table") if container else None  # 修正 'tabel' typo

    if not target_table:
        print("No data found in the specified table.")
        return None

    log_data = []

    for row in target_table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) < 9 or "Date" in cols[0]:  # 跳過表頭
            continue
        try:
            row_dt = datetime.strptime(cols[0], "%Y/%m/%d %H:%M:%S")

            if row_dt.strftime("%Y/%m/%d") == target_date:
                temp_c_part = cols[8].split(" ")[0].strip() if " " in cols[8] else cols[8]
                temp_c_clean = ''.join(c for c in temp_c_part if c.isdigit() or c == '.')

                row_data = {
                    "DateTime": row_dt.strftime("%Y/%m/%d %H:%M:%S"),
                    "Vin": cols[1],
                    "Vout": cols[2],
                    "Freq": cols[3],
                    "Load": cols[4],
                    "Capacity": cols[5],
                    "BatteryVolt": cols[6],
                    "CellVolt": cols[7],
                    "Temp": temp_c_clean
                }

                log_data.append(row_data)

        except ValueError as e:
            print(f"Row skipped due to time parsing error: {e}")
            continue

    return log_data if log_data else None


if __name__ == "__main__":
    url = "http://172.21.2.13/DataLog.cgi"
    username = "admin"
    password = "misadmin"
    target_date = "2025/06/11"

    data = get_html_content(url, username, password, target_date)

    if data:
        
        print(f"✅ Total rows for {target_date}: {len(data)}")
        for row in data[:3]:  # 預覽前 3 筆
            print(row)
    else:
        print("⚠ No data found.")
