import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from datetime import datetime
import getpass
import time
import re


url = "http://172.21.3.11/cgi-bin/dnpower.cgi?page=42&"
password = "misadmin"
username = "admin"

responde = requests.get(url, auth=(username, password))
soup = BeautifulSoup(responde.content, 'html.parser')

def get_current_time():
    """Get the current time in a readable format"""
    return datetime.now().strftime("%Y%m%d%H%M")

CSV_FILE_PATH = f"ups_data_{get_current_time()}.csv"
