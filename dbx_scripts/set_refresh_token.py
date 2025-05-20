import requests
import json

def refresh_access_token_and_update_config(config_path="config.json"):
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    dropbox = config["dropbox"]
    
    token_url = "https://api.dropboxapi.com/oauth2/token"
    refresh_token = dropbox["refresh_token"]
    client_id = "tvoghv83iaxuo00"
    client_secret = "yf9cuds6ntg1dv3"

    response = requests.post(token_url, data={
        "grant_type":"refresh_token",
        "refresh_token":refresh_token},
        auth=(client_id, client_secret))

    if response.ok:
        new_access_token = response.json()["access_token"]
        config["dropbox"]["access_token"] = new_access_token
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
            
            print("the token already updated.")
            return new_access_token
    else:
        print("access_token failed: ", response.text)
    