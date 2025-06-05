import pandas as pd
import os

# Example data (replace with your actual UPS data)
data = [
    {'name': 'Alice', 'age': 25, 'city': 'New York'},
    {'name': 'Bob', 'age': 30, 'city': 'San Francisco'}
]
df = pd.DataFrame(data)

# Define the OneDrive path correctly (fix the error)
onedrive_path = r'C:\Users\kuose\OneDrive - ViewSonic Corporation'  # Directly assign the path as a string
target_folder = os.path.join(onedrive_path, 'UPS_Datalog Upload')  # Use os.path.join to build the full path
csv_filename = os.path.join(target_folder, 'ups_data_05152025.csv')  # File name with today's date (May 15, 2025)

# Ensure the folder exists
os.makedirs(target_folder, exist_ok=True)

# Save CSV to the OneDrive folder
df.to_csv(csv_filename, index=False, encoding='utf-8')
# Print confirmation message
print(f"CSV saved to {csv_filename}")