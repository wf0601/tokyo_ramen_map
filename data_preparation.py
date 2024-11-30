import pandas as pd 
import glob 
import os 

orig_data_folder = 'orig_data'

# Iterate through all files in the folder
for file_name in os.listdir(orig_data_folder):
    if file_name.endswith('.csv'):  # Process only CSV files
        file_path = os.path.join(orig_data_folder, file_name)
        print(file_path)
        print(file_name)
        
        # Extract the 'type' from the file name (word before 'tokyo' and 'restaurant')
        type_parts = file_name.split('_')
        file_type = next((word for word in type_parts if word not in ['tokyo', 'restaurant', '']), None)

        # Read the CSV file
        df = pd.read_csv(file_path)

        # Add the 'type' column
        df['type'] = file_type
        
        df_filtered = df.iloc[:100]
        df_filtered = df_filtered.query('rating>=3.5')



        # Avoid duplicate rows
        file_name = '2024_'+file_name
        df_filtered = df_filtered.drop_duplicates()
        new_path = os.path.join('data', file_name)
        df_filtered.to_csv(new_path,index=False,encoding='utf-8-sig')
        