import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from datetime import datetime
import schedule
import time

# 取得並篩選HTML資料
def get_html_content(url, username, password, target_hour=8, target_minute=0, delta_minutes=45):
    response = requests.get(url, auth=(username, password))
    soup = BeautifulSoup(response.content, 'html.parser')

    expected_headers = ['Date', 'Time', 'Vin', 'Vout', 'Vbat', 'Fin', 'Fout', 'Load', 'Temp']
    tables = soup.find_all('table')

    today_date = datetime.today().date()
    target_time = datetime.combine(today_date, datetime.strptime(f"{target_hour}:{target_minute}", "%H:%M").time())

    for table in tables:
        first_row = table.find('tr')
        if not first_row:
            continue

        header_cells = first_row.find_all(['th', 'td'])
        headers = [cell.text.strip() for cell in header_cells]

        if any(expected in headers for expected in expected_headers):
            data = []
            rows = table.find_all('tr')[1:]  # Skip header row

            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= len(expected_headers):
                    date_str = cells[0].text.strip()
                    time_str = cells[1].text.strip()

                    try:
                        row_datetime = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %H:%M:%S")

                        if row_datetime.date() == today_date:
                            time_diff = abs((row_datetime - target_time).total_seconds()) / 60

                            if time_diff <= delta_minutes:
                                row_data = {}
                                for i, header in enumerate(expected_headers[:len(cells)]):
                                    row_data[header] = cells[i].text.strip()
                                data.append(row_data)
                    except ValueError:
                        print(f"Skipping invalid datetime format: {date_str} {time_str}")

            return data

    print("Could not find the expected data table in the HTML file.")
    return None

# 儲存CSV
def save_to_csv(data, filename=None):
    if not data:
        print("No data to save")
        return False

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ups_data_{timestamp}.csv"

    try:
        fieldnames = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"Data successfully saved to {filename}")

        df = pd.DataFrame(data)
        print("\nData Preview:")
        print(df.head())

        return True
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
        return False

# 要排程的主要任務
def scheduled_ups_job():
    print("process running...")

    ups_list = [
        {"name":"UPS_9F","url":"http://172.21.3.11/cgi-bin/dnpower.cgi?page=42&"},
        {"name":"UPS_8F","url":"http://172.21.4.10/cgi-bin/dnpower.cgi?page=42&"},
        {"name":"UPS_7F","url":"http://172.21.6.10/cgi-bin/dnpower.cgi?page=42&"},
        {"name":"UPS_3F","url":"http://172.21.5.14/cgi-bin/dnpower.cgi?page=42&"}
    ]
    ups_username = "admin"
    ups_password = "misadmin"

    # target time
    ups_target_hour = 8
    ups_target_mins = 30
    ups_time_range = 45

    for ups in ups_list:
        ups_name = ups["name"]
        url = ups["url"]

        data = get_html_content(url,ups_username,ups_password, ups_target_hour, ups_target_mins, ups_time_range)

        if data:
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"{ups_name}_{timestamp}_datalog.csv"
            save_to_csv(data, filename)

        else:
            print(f"No matching data found for {ups_name} today.")

schedule.every().day.at("9:00").do(scheduled_ups_job)

print("UPS Data Scheduler is running...")

while True:
    schedule.run_pending()
    time.sleep(1)
