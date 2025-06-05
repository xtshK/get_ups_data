# utils.py

import os
import pandas as pd
from datetime import datetime
from logger import logger
import config

def save_data_to_csv(data, filename=None):
    """
    儲存資料為 CSV 檔案至 config.TEMP_CSV_FOLDER
    傳回檔案完整路徑
    """
    if not data:
        logger.warning("No data to save. Received empty or None data.")
        raise ValueError("No data to save")

    # 自動命名檔案
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ups_data_{timestamp}.csv"

    folder = config.TEMP_CSV_FOLDER
    os.makedirs(folder, exist_ok=True)

    full_path = os.path.join(folder, filename)

    try:
        df = pd.DataFrame(data)
        df.to_csv(full_path, index=False, encoding='utf-8')

        logger.info(f"CSV saved to {full_path}")
        logger.debug(f"CSV preview:\n{df.head().to_string(index=False)}")
        return full_path

    except Exception as e:
        logger.error(f"Error saving CSV to {full_path}: {e}")
        raise
