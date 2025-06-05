# uploader.py

import requests
import dropbox
import os
from logger import logger  # 使用你統一的 logger 來記錄資訊
import config  # 從 config 讀取 token 設定

def refresh_access_token(refresh_token, client_id, client_secret):
    """
    根據 Refresh Token 取得新的 Dropbox Access Token
    """
    token_url = "https://api.dropboxapi.com/oauth2/token"

    try:
        response = requests.post(
            token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            },
            auth=(client_id, client_secret)
        )
        response.raise_for_status()
        new_access_token = response.json()["access_token"]
        logger.info("Dropbox token refreshed successfully.")
        return new_access_token
    except Exception as e:
        logger.error(f"Failed to refresh Dropbox token: {e}")
        raise


def upload_to_dropbox(file_path, access_token, dropbox_folder="/ups_datalog/"):
    """
    上傳指定檔案到 Dropbox 資料夾
    """
    try:
        csv_filename = os.path.basename(file_path)
        dropbox_path = os.path.join(dropbox_folder, csv_filename)
        dbx = dropbox.Dropbox(access_token)

        with open(file_path, "rb") as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

        logger.info(f"File uploaded to Dropbox: {dropbox_path}")
    except Exception as e:
        logger.error(f"Error uploading file to Dropbox: {e}")
        raise
