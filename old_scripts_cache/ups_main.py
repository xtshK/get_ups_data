import requests
import os
import pandas as pd
import dropbox 
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_html_content(url,username,password, targer_hour,target_mins, time_range):

    response = requests.get(url,auth=(username,password))
    soup = BeautifulSoup(response.content, 'html.parser')
        
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

def get_10f_data(url, username, password, target_hour, target_mins, tolerance_minutes=40):
    datalog_url = f"{url}/DataLog.cgi"
    refresh_url = f"{url}/refresh_data.cgi"

    session = requests.Session()
    session.auth = (username, password)

    try:
        session.get(refresh_url, params={"data_date": datetime.now().strftime("%Y%m%d")})
        response = session.get(datalog_url)
        response.raise_for_status()
    except Exception as e:
        print(f"failed to fetch data from {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    container = soup.find("div", id="myTab1_Content0")
    target_table = container.find("table") if container else None

    if not target_table:
        print("No target table found in the HTML content.")
        return None

    # 建立今天的目標時間（包含日期）
    target_datetime = datetime.strptime(
        f"{datetime.now().strftime('%Y/%m/%d')} {target_hour}:{target_mins}:00",
        "%Y/%m/%d %H:%M:%S"
    )
    time_tolerance = timedelta(minutes=tolerance_minutes)

    log_data = []
    for row in target_table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) < 9:
            continue
        try:
            row_dt = datetime.strptime(cols[0], "%Y/%m/%d %H:%M:%S")
            if abs(row_dt - target_datetime) <= time_tolerance:
                temp_c_part = cols[8].split(" ")[0].strip() if " " in cols[8] else cols[8]
                temp_c_clean = ''.join(c for c in temp_c_part if c.isdigit() or c == '.')

                log_data.append({
                    "DateTime": row_dt.strftime("%Y/%m/%d %H:%M:%S"),
                    "Vin": cols[1],
                    "Vout": cols[2],
                    "Freq": cols[3],
                    "Load": cols[4],
                    "Capacity": cols[5],
                    "BatteryVolt": cols[6],
                    "CellVolt": cols[7],
                    "Temp": temp_c_clean
                })
        except ValueError:
            continue

    return log_data if log_data else None

def save_to_csv(data, csv_filename=None):
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
        df.to_csv(full_csv_path, index=False, encoding='utf-8')
        print(f"CSV saved to {full_csv_path}")
        print("\nData Preview:")
        print(df.head())
        return True,full_csv_path
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
        return False
    
def refresh_access_token_and_update_config():
    
    token_url = "https://api.dropboxapi.com/oauth2/token"
    refresh_token = "X5ME8u9_8CIAAAAAAAAAAWN_7QBPvYjklLeAbZjhmXERrlJa3tnIUqU7BP9JkJtb"
    client_id = "tvoghv83iaxuo00"
    client_secret = "yf9cuds6ntg1dv3"

    response = requests.post(token_url, data={
        "grant_type":"refresh_token",
        "refresh_token":refresh_token},
        auth=(client_id, client_secret))

    if response.ok:
        # Parse the new access token from the response
        new_access_token = response.json()["access_token"]

        print("the token already updated.")
        return new_access_token
    
    else:
        print("access_token failed: ", response.text)


ACCESS_TOKEN = refresh_access_token_and_update_config()


def upload_to_dropbox(file_path,access_token, dropbox_folder="/ups_datalog/"):
    csv_filename = os.path.basename(file_path)
    dropbox_path = os.path.join(dropbox_folder,csv_filename)  # Ensure no trailing slash
 
    dbx = dropbox.Dropbox(access_token)

    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
    print(f"File {csv_filename} uploaded to Dropbox at {dropbox_path}")



if __name__ == "__main__":

    ups_list = [
        {"name": "UPS_9F", "url": "http://172.21.3.11/cgi-bin/dnpower.cgi?page=42&"},
        {"name": "UPS_8F", "url": "http://172.21.4.10/cgi-bin/dnpower.cgi?page=42&"},
        {"name": "UPS_7F", "url": "http://172.21.6.10/cgi-bin/dnpower.cgi?page=42&"},
        {"name": "UPS_3F", "url": "http://172.21.5.14/cgi-bin/dnpower.cgi?page=42&"},
        {"name": "UPS_10F", "url": "http://172.21.2.13", "is_10f": True}
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
        is_10f = ups.get("is_10f", False)

        if is_10f:
            target_time_str = f"{ups_target_hour}:{ups_target_mins}:00"
            data = get_10f_data(url, ups_username, ups_password, ups_target_hour, ups_target_mins, ups_time_range)
        else:
            data = get_html_content(url, ups_username, ups_password, ups_target_hour, ups_target_mins, ups_time_range)

        if data:
            timestamp = datetime.now().strftime("%Y%m%d")
            csv_filename = f"{ups_name}_{timestamp}_datalog.csv"
            for row in data:
                row["ups_name"] = ups_name

            # 儲存到暫存目錄中，而非 OneDrive
            temp_folder = os.path.join(os.getcwd(), "temp_csv")
            os.makedirs(temp_folder, exist_ok=True)
            full_csv_path = os.path.join(temp_folder, csv_filename)

            try:
                df = pd.DataFrame(data)
                df.to_csv(full_csv_path, index=False, encoding='utf-8')
                print(f"CSV saved to {full_csv_path}")
                print("\nData Preview:")
                print(df.head())

                access_token = refresh_access_token_and_update_config()
                if access_token:
                    upload_to_dropbox(full_csv_path, access_token)
            except Exception as e:
                print(f"Error saving/uploading CSV: {e}")
        else:
            print(f"No matching data found for {ups_name} today.")
        