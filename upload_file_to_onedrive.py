import pandas as pd
import os

data =[{'Date': '05/15/2025', 'Time': '07:48:58', 'Vin': '224', 'Vout': '230', 'Vbat': '272.2', 'Fin': '59.9', 'Fout': '60.0', 'Load': '024', 'Temp': '23'}, {'Date': '05/15/2025', 'Time': '08:48:58', 'Vin': '220', 'Vout': '230', 'Vbat': '272.2', 'Fin': '60.0', 'Fout': '60.0', 'Load': '023', 'Temp': '23'}]

df = pd.DataFrame(data)

onedrive_path = r'C:\Users\kuose\OneDrive - ViewSonic Corporation'
target_folder = os.path.join(onedrive_path,'UPS_Datalog Upload')

csv_file = os.path.join(target_folder,'output.csv')

os.makedirs(target_folder,exist_ok=True)

df.to_csv(csv_file, index=False, encoding='utf-8')
print(f"CSV saved to {csv_file}")