import logging
import os
from datetime import datetime

# 產生 logs 資料夾（若不存在）
log_folder = os.path.join(os.getcwd(), "logs")
os.makedirs(log_folder, exist_ok=True)

# 使用日期產生檔名
today_str = datetime.now().strftime("%Y%m%d")
log_filename = f"ups_log_{today_str}.txt"
log_path = os.path.join(log_folder, log_filename)

# 設定 logging
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"  # a = append, w = overwrite
)

logger = logging.getLogger(__name__)
