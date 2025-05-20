import os
from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import DataLakeServiceClient

# Load Azure AD credentials from environment (or configure directly in a secure manner)
tenant_id = os.getenv("FABRIC_TENANT_ID")
client_id = os.getenv("FABRIC_CLIENT_ID")
client_secret = os.getenv("FABRIC_CLIENT_SECRET")
if not all([tenant_id, client_id, client_secret]):
    raise Exception("Please set FABRIC_TENANT_ID, FABRIC_CLIENT_ID, and FABRIC_CLIENT_SECRET environment variables.")

# Authenticate with Azure AD using the service principal
credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

# Define target OneLake location
workspace_name = "MyWorkspace"         # Fabric workspace name
lakehouse_name = "MyLakehouse"         # Lakehouse (or other item) name (without the .lakehouse suffix)
local_file_path = "ups_data.json"      # Path to the UPS data file to upload (from Part 1)
onelake_file_name = "ups_data.json"    # The name for the file in OneLake (could be same as local file name)
target_folder = ""                     # Optional subfolder in the Lakehouse Files (e.g., "UPSLogs"). Empty for root.

# Create DataLake service client for OneLake account (OneLake uses a fixed account URL)
service_client = DataLakeServiceClient(
    account_url="https://onelake.dfs.fabric.microsoft.com/",
    credential=credential
)
# Get the filesystem (container) for the workspace
file_system_client = service_client.get_file_system_client(file_system=workspace_name)
# Build the path to the Lakehouse's Files directory
oneLake_path = f"{lakehouse_name}.lakehouse/Files"
if target_folder:
    oneLake_path += f"/{target_folder}"
# Get a client for the target directory in OneLake
directory_client = file_system_client.get_directory_client(oneLake_path)

# Upload the file to OneLake
file_client = directory_client.get_file_client(onelake_file_name)
with open(local_file_path, "rb") as data_file:
    file_client.upload_data(data_file, overwrite=True)
print(f"Uploaded {local_file_path} to OneLake folder: {lakehouse_name}.lakehouse/Files/{target_folder or '[root]'}")
