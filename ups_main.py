import requests
from bs4 import BeautifulSoup
import os
import csv
import pandas as pd
from datetime import datetime, timedelta

# get html content
def get_html_content(url, username, password, *_):
    response = requests.get(url, auth=(username, password))
    soup = BeautifulSoup(response.content, 'html.parser')

    expected_headers = ['Date', 'Time', 'Vin', 'Vout', 'Vbat', 'Fin', 'Fout', 'Load', 'Temp']
    tables = soup.find_all('table')

    for table in tables:
        first_row = table.find('tr')
        if not first_row:
            continue

        header_cells = first_row.find_all(['th', 'td'])
        headers = [cell.text.strip() for cell in header_cells]

        if any(expected in headers for expected in expected_headers):
            data = []
            rows = table.find_all('tr')[1:]

            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= len(expected_headers):
                    try:
                        row_data = {}
                        for i, header in enumerate(expected_headers[:len(cells)]):
                            row_data[header] = cells[i].text.strip()

                        if 'Date' in row_data and 'Time' in row_data:
                            row_data['DateTime'] = f"{row_data['Date']} {row_data['Time']}"
                            del row_data['Date']
                            del row_data['Time']

                        for col in ['Capacity', 'CellVolt']:
                            if col not in row_data:
                                row_data[col] = ""

                        data.append(row_data)
                    except Exception as e:
                        print(f"Skipping row due to error: {e}")
            return data

    print("Could not find expected data table in HTML.")
    return None


def save_to_csv(data, csv_filename=None):
    """Save the extracted data to a CSV file"""
    if not data:
        print("No data to save")
        return False
    
    onedrive_base_path = r'C:\Users\kuose\OneDrive - ViewSonic Corporation'
    target_folder = os.path.join(onedrive_base_path, 'UPS_Datalog Upload')
    os.makedirs(target_folder, exist_ok=True)

    if not csv_filename:
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        csv_filename = f"ups_data_{timestamp}.csv"
    
    full_csv_path = os.path.join(target_folder, csv_filename)

    try:
        df = pd.DataFrame(data)

        # ✅ 將 DateTime 欄位移到第一欄
        if "DateTime" in df.columns:
            cols = df.columns.tolist()
            cols.insert(0, cols.pop(cols.index("DateTime")))
            df = df[cols]

        if "Load" in df.columns:
            df["Load"] = df["Load"].astype(str).str.lstrip("0")

        df.to_csv(full_csv_path, index=False, encoding='utf-8')
        print(f"CSV saved to {full_csv_path}")

        print("\nData Preview:")
        print(df.head())
        return True

    except Exception as e:
        print(f"Error saving data to CSV: {e}")
        return False


if __name__ == "__main__":
    print("process running...")

    ups_list = [
        {"name":"UPS_9F","url":"http://172.21.3.11/cgi-bin/dnpower.cgi?page=42&"},
        {"name":"UPS_8F","url":"http://172.21.4.10/cgi-bin/dnpower.cgi?page=42&"},
        {"name":"UPS_7F","url":"http://172.21.6.10/cgi-bin/dnpower.cgi?page=42&"},
        {"name":"UPS_3F","url":"http://172.21.5.14/cgi-bin/dnpower.cgi?page=42&"},
        {"mame":"UPS_10F","url":"http://172.21.2.13/DataLog.cgi"}
    ]

    ups_username = "admin"
    ups_password = "misadmin"

    # target time
    ups_target_hour = 13
    ups_target_mins = 30
    ups_time_range = 45

    for ups in ups_list:
        ups_name = ups["name"]
        url = ups["url"]

        data = get_html_content(url,ups_username,ups_password, ups_target_hour, ups_target_mins, ups_time_range)

        if data:
            timestamp = datetime.now().strftime("%Y%m%d")
            csv_filename = f"{ups_name}_{timestamp}_datalog.csv"
            save_to_csv(data, csv_filename)

        else:
            print(f"No matching data found for {ups_name} today.")
