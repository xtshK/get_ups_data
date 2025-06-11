import os

UPS_LIST = [
    {"name": "UPS_9F",  "url": "http://172.21.3.11/cgi-bin/dnpower.cgi?page=42&"},
    {"name": "UPS_8F",  "url": "http://172.21.4.10/cgi-bin/dnpower.cgi?page=42&"},
    {"name": "UPS_7F",  "url": "http://172.21.6.10/cgi-bin/dnpower.cgi?page=42&"},
    {"name": "UPS_3F",  "url": "http://172.21.5.14/cgi-bin/dnpower.cgi?page=42&"},
    {"name": "UPS_10F", "url": "http://172.21.2.13", "is_10f": True},
]

UPS_USERNAME = "admin"
UPS_PASSWORD = "misadmin"

TARGET_HOUR = 00
TARGET_MINUTE= 00
TIME_RANGE_MINUTES = 1440

TEMP_CSV_FOLDER = os.path.join(os.getcwd(), 'temp_csv')

DROPBOX_REFRESH_TOKEN = "X5ME8u9_8CIAAAAAAAAAAWN_7QBPvYjklLeAbZjhmXERrlJa3tnIUqU7BP9JkJtb"
DROPBOX_APP_KEY = "tvoghv83iaxuo00"
DROPBOX_APP_SECRET = "yf9cuds6ntg1dv3"
DROPBOX_UPLOAD_PATH = "/ups_datalog/"

