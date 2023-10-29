import pandas as pd
#import numpy as np

# I import the weather data for Archalochori during the whole year of 2022
#data start the 01/01/2022 and at index 0 is the 1st hour of that day from 00:00 to 01:00
#consequently at index 1 is the 2nd hour of that day from 01:00 to 02:00 and so on

# Load the data Series from the Excel file
ghi_Archal = pd.read_excel('ghi_Archalochori.xlsx')
ambTemp_Archal = pd.read_excel('Air Temp_Archalochori.xlsx')

# Convert the DataFrame column to a NumPy array
ghi_nparray = ghi_Archal['Ghi'].values
ambTemp_nparray = ambTemp_Archal['AirTemp'].values

# Convert the DataFrame column to a list
#ghi_nparray = ghi_Archal['Ghi'].tolist()
#ambTemp_nparray = ambTemp_Archal['AirTemp'].tolist()

#b = ghi_nparray + ambTemp_nparray
 
