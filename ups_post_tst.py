import requests
import openpyxl
from requests.auth import HTTPBasicAuth
import pandas as pd
from io import StringIO


ups_targets = {
    {"name": "UPS_9F",  "url": "http://172.21.3.11/cgi-bin/dnpower.cgi?page=42&"},
    {"name": "UPS_8F",  "url": "http://172.21.4.10/cgi-bin/dnpower.cgi?page=42&"},
    {"name": "UPS_7F",  "url": "http://172.21.6.10/cgi-bin/dnpower.cgi?page=42&"},
    {"name": "UPS_3F",  "url": "http://172.21.5.14/cgi-bin/dnpower.cgi?page=42&"}
}

base_url = "http://172.21.5.14"
download_url = f"{base_url}/cgi-bin/datalog.csv?page=421&"

session = requests.Session()
# 先嘗試 GET 初始化連線（非必要但保險）
session.get(base_url, auth=HTTPBasicAuth("admin", "misadmin"))

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": base_url
}

# 🔥 核心關鍵：帶入表單欄位 GETDATFILE=Download
form_data = {
    "GETDATFILE": "Download"
}

# 改用 multipart/form-data 上傳格式
response = session.post(
    download_url,
    headers=headers,
    files={"GETDATFILE": (None, "Download")},  # 用 multipart/form-data 格式送出
    auth=HTTPBasicAuth("admin", "misadmin")
)

# 儲存資料
if response.status_code == 200 and len(response.content) > 100:
    decoded = response.content.decode("utf-8")
    df = pd.read_csv(StringIO(decoded), header=None)
    df.columns = ["Date", "Time", "Vin", "Vout", "Vbat", "Fin", "Fout", "Load", "Temp"]
    
    df.to_csv("ups_3f_full_log_clean.csv", index=False)
    # df.to_excel("ups_9f_full_log_clean.xlsx", index=False)
    print("✅ 已用 pandas 轉換並儲存整天 UPS 資料")
    
else:
    print("❌ 下載失敗")
    print("狀態碼:", response.status_code)
    print("回應內容:", response.text[:500])
