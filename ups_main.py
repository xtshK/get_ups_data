import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from datetime import datetime

# get html content
def get_html_content(url,username,password):
    responde = requests.get(url,auth=(username,password))
    soup = BeautifulSoup(responde.content, 'html.parser')
        
        # Expected headers based on your screenshot
    expected_headers = ['Date', 'Time', 'Vin', 'Vout', 'Vbat', 'Fin', 'Fout', 'Load', 'Temp']
        
        # Find all tables in the page
    tables = soup.find_all('table')
        
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
                        row_data = {}
                        for i, header in enumerate(expected_headers[:len(cells)]):
                            row_data[header] = cells[i].text.strip()
                        data.append(row_data)
                
                return data
        
    print("Could not find the expected data table in the HTML file.")
    return None

def save_to_csv(data, filename=None):
    """Save the extracted data to a CSV file"""
    if not data:
        print("No data to save")
        return False
    
    if not filename:
        # Generate a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

if __name__ == "__main__":
    print("process running...")
    ups_url = "http://172.21.4.10/cgi-bin/dnpower.cgi?page=42&"
    ups_username = "admin"
    ups_password = "misadmin"

    data = get_html_content(ups_url,ups_username,ups_password)

    if data:
        save_to_csv(data)
    else:
        print("save_to_csv run failed.")