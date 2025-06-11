import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from io import StringIO
import os

# 樓層與對應 URL
ups_targets = [
    {"name": "UPS_9F", "url": "http://172.21.3.11"},
    {"name": "UPS_8F", "url": "http://172.21.4.10"},
    {"name": "UPS_7F", "url": "http://172.21.6.10"},
    {"name": "UPS_3F", "url": "http://172.21.5.14"}
]

# 登入資訊
username = "admin"
password = "misadmin"

# 儲存路徑
output_dir = "ups_logs"
os.makedirs(output_dir, exist_ok=True)

# 開始爬每一台 UPS
for ups in ups_targets:
    ups_name = ups["name"]
    base_url = ups["url"]
    download_url = f"{base_url}/cgi-bin/datalog.csv?page=421&"

    print(f"📡 正在下載 {ups_name} 的 UPS 資料...")

    session = requests.Session()
    session.get(base_url, auth=HTTPBasicAuth(username, password))

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": base_url
    }
    form_data = {
        "GETDATFILE": "Download"
    }

    response = session.post(
        download_url,
        headers=headers,
        data=form_data,
        auth=HTTPBasicAuth(username, password)
    )

    if response.status_code == 200 and len(response.content) > 100:
        decoded = response.content.decode("utf-8", errors="ignore")

        try:
            df = pd.read_csv(StringIO(decoded), header=None)
            df.columns = ["Date", "Time", "Vin", "Vout", "Vbat", "Fin", "Fout", "Load", "Temp"]
            df["UPS_Name"] = ups_name  # ✅ 把 UPS name 加進去
            df = df[[*df.columns[:-1], "UPS_Name"]]  # 確保 UPS_Name 是最後一欄

            df.to_csv(f"{output_dir}/{ups_name}_log.csv", index=False)
            
            print(f"✅ {ups_name} 資料儲存成功，共 {len(df)} 筆")
        except Exception as e:
            print(f"⚠️ {ups_name} 轉換失敗：{e}")
    else:
        print(f"❌ {ups_name} 下載失敗（狀態碼 {response.status_code}）")
        print("內容預覽：", response.text[:200])
