import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from datetime import datetime
import getpass
import time
import re

def login_to_power_device(url, username, password):
    """Log in to the PowerDevice Manager and return the authenticated session"""
    session = requests.Session()
    
    # First visit the login page
    login_page = session.get(url)
    
    # Check if we got the page
    if login_page.status_code != 200:
        print(f"Failed to access login page. Status code: {login_page.status_code}")
        return None
        
    # Find the login form - you may need to inspect the actual form on the page
    soup = BeautifulSoup(login_page.content, 'html.parser')
    
    # Prepare login data - adjust field names based on the actual form
    login_data = {
        'username': username,
        'password': password
    }
    
    # The login URL might be different from the initial URL
    # You may need to extract it from the form action or use a known endpoint
    login_endpoint = url + "/login"  # Adjust as needed
    
    # Perform login
    response = session.post(login_endpoint, data=login_data)
    
    # Check if login was successful - this needs to be adjusted based on the actual behavior
    if response.status_code == 200 and "login failed" not in response.text.lower():
        print("Login successful!")
        return session
    else:
        print(f"Login failed. Status code: {response.status_code}")
        return None

def get_data_log_table(session, url):
    """Navigate to the Data Log page and extract the table data"""
    # Navigate to the Data Log page - adjust URL as needed
    data_log_url = url + "/Log/DataLog"  # Adjust based on actual URL structure
    
    response = session.get(data_log_url)
    
    if response.status_code != 200:
        print(f"Failed to access Data Log page. Status code: {response.status_code}")
        return None
    
    # Parse the HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the data table - you'll need to adjust these selectors based on the actual HTML structure
    # Based on your screenshot, this might be a table with specific attributes
    table = soup.find('table', {'width': '100%'}) or soup.find('table', {'cellspacing': '0'})
    
    if not table:
        # Try alternative methods to locate the table
        tables = soup.find_all('table')
        if tables and len(tables) > 1:
            # Since there are multiple tables, we need to identify the right one
            # This is a guess based on your screenshot - you might need to adjust
            table = tables[1]  # The second table appears to be the data log
    
    if not table:
        print("Could not find the data log table in the page.")
        return None
    
    # Extract the table headers
    headers = []
    header_row = table.find('tr')
    if header_row:
        headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
    
    # Extract the table data
    data = []
    data_rows = table.find_all('tr')[1:]  # Skip the header row
    for row in data_rows:
        row_data = [td.text.strip() for td in row.find_all('td')]
        if row_data:  # Only add non-empty rows
            data.append(dict(zip(headers, row_data)))
    
    return data

def save_to_csv(data, filename=None):
    """Save the extracted data to a CSV file"""
    if not data:
        print("No data to save")
        return False
    
    if not filename:
        # Generate a filename with timestamp if none provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"power_device_data_{timestamp}.csv"
    
    try:
        # Get field names from the first item in the data
        fieldnames = data[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Data successfully saved to {filename}")
        
        # Also create a pandas DataFrame and show a preview
        df = pd.DataFrame(data)
        print("\nData Preview:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
        return False

def extract_data_from_html_page(html_content):
    """Alternative method to extract data directly from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Based on your screenshot, these seem to be the column headers
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
    
    return None

def main():
    print("PowerDevice Manager Data Scraper")
    print("===============================")
    
    # Get user input
    device_url = "http://172.21.3.11/cgi-bin/dnpower.cgi?page=42&"
    username = "admin"
    password = "misadmin"
    
    # Option for direct HTML input if login doesn't work
    use_html = "2"

    if use_html == "1":
        # Try automatic login and scraping
        session = login_to_power_device(device_url, username, password)
        if not session:
            print("Login failed. You can try manual HTML input instead.")
            return
        
        # Get data log table
        data = get_data_log_table(session, device_url)
        
        if not data:
            print("Failed to extract data from the table.")
            return
            
        # Save to CSV
        save_to_csv(data)
        
    elif use_html == "2":

        html_content = ""
        
        while True:
            line = input()
            if line == "":
                break
            html_content += line + "\n"
        
        if not html_content:
            print("No HTML content provided.")
            return
            
        # Extract data from HTML
        data = extract_data_from_html_page(html_content)
        
        if not data:
            print("Failed to extract data from the provided HTML.")
            return
            
        # Save to CSV
        save_to_csv(data)
    else:
        print("Invalid option selected.")

if __name__ == "__main__":
    main()