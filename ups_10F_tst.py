import requests
from bs4 import BeautifulSoup
import os
import csv
import pandas as pd
from datetime import datetime, timedelta

def get_html_content(url, username, password, target_hour, target_mins, time_range):

    response = requests.get(url,auth=(username,password))
    soup = BeautifulSoup(response.content, 'html.parser')








if __name__ == "__main__":
    ups = "http://172.21.2.13/DataLog.cgi"

    username = "admin"
    password = "misadmin"

    # target time
    ups_target_hour = 13
    ups_target_mins = 30
    ups_time_range = 45

