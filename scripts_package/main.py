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
    Main process: iterate through UPS_LIST, extract data, save CSV, and upload to Dropbox.
    """
    os.makedirs(config.TEMP_CSV_FOLDER, exist_ok=True)

    for ups in config.UPS_LIST:
        ups_name = ups["name"]
        url = ups["url"]
        is_10f = ups.get("is_10f", False)

        logger.info(f"Processing started for {ups_name}")

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
            logger.error(f"{ups_name}: Failed to fetch data - {e}")
            continue

        if not data:
            logger.warning(f"{ups_name}: No matching data found in the specified time range.")
            continue

        for row in data:
            row["ups_name"] = ups_name

        timestamp = datetime.now().strftime("%Y%m%d")
        csv_filename = f"{ups_name}_{timestamp}_datalog.csv"

        try:
            full_path = save_data_to_csv(data, csv_filename)
            logger.info(f"{ups_name}: CSV saved successfully → {full_path}")
        except Exception as e:
            logger.error(f"{ups_name}: Failed to save CSV - {e}")
            continue

        try:
            access_token = refresh_access_token(
                config.DROPBOX_REFRESH_TOKEN,
                config.DROPBOX_APP_KEY,
                config.DROPBOX_APP_SECRET
            )
        except Exception as e:
            logger.error(f"{ups_name}: Failed to refresh Dropbox token - {e}")
            continue

        try:
            upload_to_dropbox(full_path, access_token, config.DROPBOX_UPLOAD_PATH)
            logger.info(f"{ups_name}: Uploaded to Dropbox → {config.DROPBOX_UPLOAD_PATH}{csv_filename}")
        except Exception as e:
            logger.error(f"{ups_name}: Failed to upload to Dropbox - {e}")

    logger.info("All UPS data processing completed.")


if __name__ == "__main__":
    logger.info("UPS Data Scheduler started (manual run)")
    process_all_ups()
