import pandas as pd
import numpy as np
import glob
#import os

#this function imports all the excels with the different demand profiles between the pros and consumers
#and imports them in an array all together, so that in the main script I can seperate which correspond to prosumers
#and which to consumers in each scenario


def find_Demand(num_days, num_hours, num_seller, num_buyer):
    
    # Define the file path pattern to match the Excel files
    file_pattern = 'house_*_new.xlsx'  # Modify the pattern to match your file names
    
    # Get the list of file paths matching the pattern
    file_paths = glob.glob(file_pattern)
    
    # Create the 3D array
    demand_hourly_total = np.zeros((num_days, num_hours, num_seller + num_buyer))
     
    # Iterate over the file paths
    
    for file_path in file_paths:
        # Extract the house number from the file name
        house_number = int(file_path.split('_')[1])
    
        # Read the Excel file and retrieve the desired column
        df = pd.read_excel(file_path)
        consumption_values = df['Consumption (kWh/hour)'].values
        
        # Iterate over the day and hour indices
        for day_index in range(num_days):
            for hour_index in range(num_hours):
                # Calculate the flat index for the demand_hourly_total array
                flat_index = day_index * num_hours + hour_index
    
                # Assign the consumption value to the corresponding cell in the 3D array
                demand_hourly_total[day_index, hour_index, house_number - 1] = consumption_values[flat_index]
                
    return demand_hourly_total
 
























