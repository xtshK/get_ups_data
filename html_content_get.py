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

print(soup.prettify())