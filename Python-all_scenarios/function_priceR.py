from function_Price_to_Pay_v5 import price
import numpy as np


def price_R(day, hour, num_buyer, num_seller, buyer_bidQuantity, seller_bidQuantity, ED_array, ES_array, 
            battery_cap, battery_cap_min, R_array, p_bal, p_con, k, ETH_2_EURO, ether, minPrice_DSO):
        
    #I need to put a for loop here until the end of the code
    #the buyer_bidQuantity needs to become an 3-by-3 array with dimensions of (day - hour - buyer)
    
    #ED = sum(buyer_bidQuantity[day][hour][agent_b] for agent_b in range(num_buyer+num_seller))  # total initial demand in kWh
    ED_array[day, hour] = np.sum(buyer_bidQuantity[day, hour, :num_buyer+num_seller]) # total initial demand in kWh 
    
    """
    #including batteries capacity in the determination of the price
    if hour == 0 and day == 0:
        ES_array[day, hour] = np.sum(seller_bidQuantity[day, hour, :num_seller]) + np.sum(battery_cap[day, hour, :num_seller]) - np.sum(battery_cap_min, axis=0) 
    elif hour > 0:
        ES_array[day, hour] = np.sum(seller_bidQuantity[day, hour, :num_seller]) + np.sum(battery_cap[day, hour-1, :num_seller]) - np.sum(battery_cap_min, axis=0) 
    elif hour == 0 and day > 0:
        ES_array[day, hour] = np.sum(seller_bidQuantity[day, hour, :num_seller]) + np.sum(battery_cap[day-1, 23, :num_seller]) - np.sum(battery_cap_min, axis=0) 
    """  
    
    # NOT including batteries capacity in the determination of the price
    ES_array[day, hour] = np.sum(seller_bidQuantity[day, hour, :num_seller])
    #initial available supply in kWh + the energy saved in batteries of sellers     
           
    ###ERROR when supply is zero / fix it
    if ES_array[day, hour] != 0:
        R = ED_array[day, hour]/ ES_array[day, hour] 
        R_array[day, hour] = R
    else:
        #R = 10**-1000 #very small value to go close to 0, check paper 4 formula 6 
        R = 10**10
        R_array[day, hour] = R
         
    #k = 3
    Price_kwh = int(price(p_bal, p_con, R, k, ETH_2_EURO, ether, minPrice_DSO)) # common price per kWh for all-function price from Price_to_Pay_v5.py file
    #Price_kwh = price(p_bal, p_con, R, k, ETH_2_EURO, ether, minPrice_DSO)  
    return Price_kwh, R, R_array, ED_array, ES_array
