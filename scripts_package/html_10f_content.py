import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_10f_data(url, username, password, target_hour, target_mins, tolerance_minutes=40):
    datalog_url = f"{url}/DataLog.cgi"
    refresh_url = f"{url}/refresh_data.cgi"

    session = requests.Session()
    session.auth = (username, password)

    try:
        session.get(refresh_url, params={"data_date": datetime.now().strftime("%Y%m%d")})
        response = session.get(datalog_url)
        response.raise_for_status()
    except Exception as e:
        print(f"failed to fetch data from {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    container = soup.find("div", id="myTab1_Content0")
    target_table = container.find("table") if container else None

    if not target_table:
        print("No target table found in the HTML content.")
        return None

    # 建立今天的目標時間（包含日期）
    target_datetime = datetime.strptime(
        f"{datetime.now().strftime('%Y/%m/%d')} {target_hour}:{target_mins}:00",
        "%Y/%m/%d %H:%M:%S"
    )
    time_tolerance = timedelta(minutes=tolerance_minutes)

    log_data = []
    for row in target_table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) < 9:
            continue
        try:
            row_dt = datetime.strptime(cols[0], "%Y/%m/%d %H:%M:%S")
            if abs(row_dt - target_datetime) <= time_tolerance:
                temp_c_part = cols[8].split(" ")[0].strip() if " " in cols[8] else cols[8]
                temp_c_clean = ''.join(c for c in temp_c_part if c.isdigit() or c == '.')

                log_data.append({
                    "DateTime": row_dt.strftime("%Y/%m/%d %H:%M:%S"),
                    "Vin": cols[1],
                    "Vout": cols[2],
                    "Freq": cols[3],
                    "Load": cols[4],
                    "Capacity": cols[5],
                    "BatteryVolt": cols[6],
                    "CellVolt": cols[7],
                    "Temp": temp_c_clean
                })
        except ValueError:
            continue

    return log_data if log_data else None