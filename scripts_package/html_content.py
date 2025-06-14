import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_html_content(url,username,password, targer_hour,target_mins, time_range):


    response = requests.get(url,auth=(username,password))
    soup = BeautifulSoup(response.content, 'html.parser')
        
        # Expected headers based on your screenshot
    expected_headers = ['Date', 'Time', 'Vin', 'Vout', 'Vbat', 'Fin', 'Fout', 'Load', 'Temp']
        
    header_mapping = {
    'Date': 'Date',
    'Time': 'Time',
    'Vin': 'Vin',
    'Vout': 'Vout',
    'Vbat': 'BatteryVolt',   # 轉換欄位
    'Fin': 'Freq',
    'Fout': 'Fout',
    'Load': 'Load',
    'Temp': 'Temp'
    }

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
                                        raw_value = cells[i].text.strip()
                                        mapped_key = header_mapping.get(header, header)
                                        row_data[mapped_key] = raw_value

                                if 'Date' in row_data and 'Time' in row_data:
                                    row_data['DateTime'] = f"{row_data['Date']} {row_data['Time']}"

                                    del row_data['Date']  # 可選：移除原始 Date
                                    del row_data['Time']  # 可選：移除原始 Time    
                                    
                                for col in ['Capacity', 'CellVolt']:
                                    if col not in row_data:
                                        row_data[col] = ""

                                data.append(row_data)

                        except ValueError:
                            print(f"Skipping invalid time format: {time_str}")

                return data
        
    print("Could not find the expected data table in the HTML file.")
    return None