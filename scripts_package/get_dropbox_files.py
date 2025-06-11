import dropbox
import requests
import pandas as pd
from datetime import datetime

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
    
new_access_token = refresh_access_token_and_update_config()

# ========== 參數設定 ==========
ACCESS_TOKEN = new_access_token  # 替換成你的 Dropbox token
DROPBOX_FOLDER = "/ups_datalog"             # Dropbox 上的資料夾
LOCAL_FOLDER = "/Files"  # Fabric Notebook 的本地暫存路徑
UPS_TABLE_NAME = "UPS_Datalog"              # Lakehouse 中的資料表名

# ========== 初始化 Dropbox ==========
dbx = dropbox.Dropbox(ACCESS_TOKEN)

# ========== 取得 Dropbox 上所有 UPS CSV ==========
print("正在列出 Dropbox 上的 UPS 檔案...")
entries = dbx.files_list_folder(DROPBOX_FOLDER).entries
csv_files = [e for e in entries if isinstance(e, dropbox.files.FileMetadata) and e.name.endswith(".csv")]

print(f"找到 {len(csv_files)} 筆 UPS 檔案")