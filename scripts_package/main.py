# main.py

import os
import pandas as pd
from datetime import datetime

from logger import logger
import config
from html_content import get_html_content
from html_10f_content import get_10f_data
from uploader import refresh_access_token, upload_to_dropbox
from utils import save_data_to_csv

def process_all_ups():
    """
    主要流程：對 config.UPS_LIST 中的每一台 UPS 進行抓取、儲存 CSV、上傳 Dropbox。
    """
    # 確認暫存 CSV 資料夾存在
    os.makedirs(config.TEMP_CSV_FOLDER, exist_ok=True)

    for ups in config.UPS_LIST:
        ups_name = ups["name"]
        url = ups["url"]
        is_10f = ups.get("is_10f", False)

        logger.info(f"開始處理 {ups_name}")

        # 根據是否是 10F UPS 呼叫不同的資料擷取函式
        try:
            if is_10f:
                data = get_10f_data(
                    url,
                    config.UPS_USERNAME,
                    config.UPS_PASSWORD,
                    config.TARGET_HOUR,
                    config.TARGET_MINUTE,
                    config.TIME_RANGE_MINUTES
                )
            else:
                data = get_html_content(
                    url,
                    config.UPS_USERNAME,
                    config.UPS_PASSWORD,
                    config.TARGET_HOUR,
                    config.TARGET_MINUTE,
                    config.TIME_RANGE_MINUTES
                )
        except Exception as e:
            logger.error(f"{ups_name} 取得資料失敗: {e}")
            continue

        # 如果沒抓到資料，就跳過
        if not data:
            logger.warning(f"{ups_name}：未擷取到符合時間條件的資料")
            continue

        # 加上 ups_name 欄位
        for row in data:
            row["ups_name"] = ups_name

        # 檔名：UPS名稱 + 日期_datalog.csv
        timestamp = datetime.now().strftime("%Y%m%d")
        csv_filename = f"{ups_name}_{timestamp}_datalog.csv"

        # 儲存到 temp_csv 資料夾
        try:
            full_path = save_data_to_csv(data, csv_filename)
            logger.info(f"{ups_name}：CSV 儲存成功 → {full_path}")
        except Exception as e:
            logger.error(f"{ups_name}：儲存 CSV 時發生錯誤: {e}")
            continue

        # 取得最新的 Dropbox Access Token
        try:
            access_token = refresh_access_token(
                config.DROPBOX_REFRESH_TOKEN,
                config.DROPBOX_APP_KEY,
                config.DROPBOX_APP_SECRET
            )
        except Exception as e:
            logger.error(f"{ups_name}：刷新 Dropbox token 失敗: {e}")
            continue

        # 上傳到 Dropbox
        try:
            upload_to_dropbox(full_path, access_token, config.DROPBOX_UPLOAD_PATH)
            logger.info(f"{ups_name}：成功上傳到 Dropbox → {config.DROPBOX_UPLOAD_PATH}{csv_filename}")
        except Exception as e:
            logger.error(f"{ups_name}：上傳到 Dropbox 失敗: {e}")

    logger.info("所有 UPS 資料處理完成。")


if __name__ == "__main__":
    # 直接執行一次，若要排程可改用 Windows Task Scheduler 來呼叫 main.py
    logger.info("UPS Data Scheduler 執行中 (手動啟動)")
    process_all_ups()
