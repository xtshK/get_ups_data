import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from logger import logger

def get_10f_data_for_date(url, username, password, target_date_str):
    """
    改為比對整天（指定日期）所有符合的 10F 資料
    """
    datalog_url = f"{url}/DataLog.cgi"
    refresh_url = f"{url}/refresh_data.cgi"

    session = requests.Session()
    session.auth = (username, password)

    try:
        session.get(refresh_url, params={"data_date": target_date_str.replace("/", "")})
        response = session.get(datalog_url)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch 10F data from {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    container = soup.find("div", id="myTab1_Content0")
    target_table = container.find("table") if container else None

    if not target_table:
        logger.warning("No target table found in the 10F UPS page.")
        return None

    log_data = []
    for row in target_table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) < 9 or "Date" in cols[0]:
            continue
        try:
            row_dt = datetime.strptime(cols[0], "%Y/%m/%d %H:%M:%S")

            # ✅ 只篩選指定日期的資料
            if row_dt.strftime("%Y/%m/%d") == target_date_str:
                temp_c_part = cols[8].split(" ")[0].strip() if " " in cols[8] else cols[8]
                temp_c_clean = ''.join(c for c in temp_c_part if c.isdigit() or c == '.')

                row_data = {
                    "DateTime": row_dt.strftime("%Y/%m/%d %H:%M:%S"),
                    "Vin": cols[1],
                    "Vout": cols[2],
                    "Freq": cols[3],
                    "Load": cols[4],
                    "Capacity": cols[5],
                    "BatteryVolt": cols[6],
                    "CellVolt": cols[7],
                    "Temp": temp_c_clean
                }

                log_data.append(row_data)

        except ValueError as ve:
            logger.warning(f"Row skipped due to time parsing error: {ve}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error while parsing 10F UPS row: {e}")
            continue

    if log_data:
        logger.info(f"✅ Found {len(log_data)} records for {target_date_str}")
        return log_data
    else:
        logger.info(f"⚠ No data found for date {target_date_str}")
        return None


if __name__ == "__main__":
    url = "http://172.21.2.13"
    username = "admin"
    password = "misadmin"
    target_date = "2025/06/10"

    data = get_10f_data_for_date(url, username, password, target_date)
    if data:
        print(f"Found {len(data)} rows.")
        for row in data[:23]:
            print(row)
