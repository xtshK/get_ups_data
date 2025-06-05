import logging
import os

log_folder = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_folder, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_folder, 'ups_log.txt'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a',
)

logger = logging.getLogger(__name__)