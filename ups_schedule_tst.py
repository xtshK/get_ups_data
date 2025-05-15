import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from datetime import datetime
import schedule
import time

# 取得並篩選HTML資料
def get_html_content(url,username,password, targer_hour,target_mins, time_range):
    responde = requests.get(url,auth=(username,password))
    soup = BeautifulSoup(responde.content, 'html.parser')
        
        # Expected headers based on your screenshot
    expected_headers = ['Date', 'Time', 'Vin', 'Vout', 'Vbat', 'Fin', 'Fout', 'Load', 'Temp']
        
        # Find all tables in the page
    tables = soup.find_all('table')

    target_time = datetime.strptime(f"{targer_hour}:{target_mins}","%H:%M")
        
        # Look for a table that has our expected data
    for table in tables:
            first_row = table.find('tr')
            if not first_row:
                continue
                
            # Check header cells
            header_cells = first_row.find_all(['th', 'td'])
            headers = [cell.text.strip() for cell in header_cells]
            
            # Check if this table has headers that match what we expect
            if any(expected in headers for expected in expected_headers):
                # Found the right table, now extract data
                data = []
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= len(expected_headers):
                        time_str = cells[1].text.strip()

                        try:
                            row_time = datetime.strptime(time_str, "%H:%M:%S")
                            time_diff = abs((row_time - target_time)).total_seconds()/60

                            if time_diff <=time_range:
                                row_data = {}

                                for i, header in enumerate(expected_headers[:len(cells)]):
                                    row_data[header] = cells[i].text.strip()
                                data.append(row_data)

                        except ValueError:
                            print(f"Skipping invalid time format: {time_str}")

                return data
        
    print("Could not find the expected data table in the HTML file.")
    return None

# 儲存CSV
def save_to_csv(data, filename=None):

    """Save the extracted data to a CSV file"""
    if not data:
        print("No data to save")
        return False
    
    if not filename:
        # Generate a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        filename = f"ups_data_{timestamp}.csv"
    
    try:
        # Get field names from the first item in the data
        fieldnames = data[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Data successfully saved to {filename}")
        
        # Create a pandas DataFrame and show a preview
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

schedule.every().day.at("16:30").do(scheduled_ups_job)

print("UPS Data Scheduler is running...")

while True:
    schedule.run_pending()
    time.sleep(1)
