import pandas as pd


# I import the weather data for Archalochori during the whole year of 2022
#data start the 01/01/2022 and at index 0 is the 1st hour of that day from 00:00 to 01:00
#consequently at index 1 is the 2nd hour of that day from 01:00 to 02:00 and so on

#data1 = pd.read_excel('solcast - data for 2022 - Archalochori.xlsx')
data2 = pd.read_csv('solcast_Archanes_2022.csv')
data3 = pd.read_csv('solcast_Herakleion_2022.csv')
data4 = pd.read_csv('solcast_Nea_Arvi_2022.csv')
#data.to_csv('data.csv', index=False)

#ghi_Archal = data1['Ghi']
#ambTemp_Archal = data1['AirTemp'] 

ghi_Archan = data2['Ghi']
ambTemp_Archan = data2['AirTemp'] 

ghi_Her = data3['Ghi']
ambTemp_Her = data3['AirTemp'] 

ghi_Arvi = data4['Ghi']
ambTemp_Arvi = data4['AirTemp'] 
 
# Save the data Series as an Excel file
#ghi_Archal.to_excel('solcast_ghi_Archalochori.xlsx', index=False)
#ambTemp_Archal.to_excel('solcast_Air Temp_Archalochori.xlsx', index=False)

ghi_Archan.to_excel('solcast_ghi_Archanes.xlsx', index=False)
ambTemp_Archan.to_excel('solcast_Air Temp_Archanes.xlsx', index=False)

ghi_Her.to_excel('solcast_ghi_Herakleion.xlsx', index=False)
ambTemp_Her.to_excel('solcast_Air Temp_Herakleion.xlsx', index=False)

ghi_Arvi.to_excel('solcast_ghi_Nea_Arvi.xlsx', index=False)
ambTemp_Arvi.to_excel('solcast_Air Temp_Nea_Arvi.xlsx', index=False)



