import requests
import json
import dropbox 
import dropbox.files

def refresh_access_token_and_update_config():
    
    token_url = "https://api.dropboxapi.com/oauth2/token"
    refresh_token = "X5ME8u9_8CIAAAAAAAAAAWN_7QBPvYjklLeAbZjhmXERrlJa3tnIUqU7BP9JkJtb"
    client_id = "tvoghv83iaxuo00"
    client_secret = "yf9cuds6ntg1dv3"

    response = requests.post(token_url, data={
        "grant_type":"refresh_token",
        "refresh_token":refresh_token},
        auth=(client_id, client_secret))

    if response.ok:
        # Parse the new access token from the response
        new_access_token = response.json()["access_token"]

        print("the token already updated.")
        return new_access_token
    
    else:
        print("access_token failed: ", response.text)


ACCESS_TOKEN = refresh_access_token_and_update_config()
dbx = dropbox.Dropbox(ACCESS_TOKEN)

print("Access token:", ACCESS_TOKEN)

# Define the filename and Dropbox path
'''
filename = "ups_log_3F ups_20250407.csv"
dropbox_path = f"/ups_datalog/{filename}"
'''