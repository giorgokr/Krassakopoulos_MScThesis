#with this function file I can calculate the price in every auction of every day of the year, based only on 
#the available supply by the prosumers and the demand
#I have considered also in every auction the energy of the batteries while being full as part of the available supply
#in every hour
#so I can find the average price of the whole year and use it as the start, for hour = 0 for the EMA in my 
#main file

#generally usefull outcome
#consodering full batteries added to supply in every auction -> Price_ave = 0.5001 euro
#consodering empty batteries added to supply in every auction -> Price_ave = 0.7877 euro

#later I added the procedure to 
 
#from Price_to_Pay_v5 import price
from function_initiateBids import initiate_Bids
from function_priceR import price_R
#import random
#from statistics import mean
import numpy as np
 

def avePrice_0(num_days, num_hours, num_seller, num_buyer, batt_ch_eff, batt_disch_eff):
      
    # vector with sellers' bid quantities 
    seller_bidQuantity = np.zeros((num_days, num_hours, num_seller))
    # vector with sellers' initial own need in energy demand (before cover by his own gen) 
    pros_dem_ini = np.random.uniform(0.5, 1.6, size=(num_days, num_hours, num_seller))    # vector with sellers' own generation
    pros_gen = np.random.uniform(1, 3, size=(num_days, num_hours, num_seller)) 
    # vector with sellers' final own need in energy demand (after cover by his own gen) 
    pros_dem_f = np.zeros((num_days, num_hours, num_seller)) 
    # vector with buyers' bid quantities (prosumers + consumers) 
    buyer_bidQuantity = np.zeros((num_days, num_hours, num_buyer+num_seller))
    # vector with consumers' demand  
    cons_dem = np.random.uniform(0.5, 1.6, size=(num_days, num_hours, num_buyer))
    
    """ 
    seller_battery = [random.randint(0 , 1) for _ in range(num_seller)] #generate randomly which sellers have batteries
    # denotes which sellers own batteries (1 owns battery - 0 no battery)
    bmax = [random.randint(5 , 10) for _ in range(num_seller)] 
    battery_cap_max = [x * y for x, y in zip(bmax, seller_battery)] # I should multiply each value with the respective seller_battery 
    #max capacity of sellers' batteries 
    battery_cap = [0 for _ in range(num_seller)] #includes the capacity of sellers' batteries - Initially they all have: 0 kWh
    # I should multiply each value with the respective seller_battery 
    """
    #About batteries  
    #seller_battery = np.random.randint(0, 2, size=num_seller) #generate randomly which sellers have batteries (gives value of 0 or 1)
    seller_battery = np.full(num_seller, 1) # num_seller is the length (columns) of the array and 1 is the value in each
    # denotes which sellers own batteries (1 owns battery - 0 no battery) 
    #bmax = np.random.randint(5, 11, size=num_seller) #The function generates random integers between 5 and 10 (inclusive) and 
    #populates the array with those values.
        
    #max capacity of sellers' batteries 
    bmax = np.full(num_seller, 5)  
    SOC_80 = 0.8 # factor for max SOC to be 80%  
    SOC_20 = 0.2 # factor for min SOC to be 20%  
    battery_cap_max = SOC_80 * np.multiply(bmax, seller_battery) #max charge level (SOC) that we allow the batteries to be
    battery_cap_min = SOC_20 * np.multiply(bmax, seller_battery) #max charge level (SOC) that we allow the batteries to be
    #battery_cap = np.full(num_seller, 0) 
    battery_cap = battery_cap_min * np.ones((num_days, num_hours, num_seller))
    # I should multiply each value with the respective seller_battery 
    
    ## Needed 2D arrays to save the ED, ES, R, and clearing prices in each auction
    #first index represents the day, second index represents the hour
    ED_array = np.zeros((num_days, num_hours)) #initial demand in kWh
    ES_array = np.zeros((num_days, num_hours)) #initial supply in kWh
    R_array = np.zeros((num_days, num_hours))
    Price_kwh_array = np.zeros((num_days, num_hours)) # clearing price in wei
    Price_kwh_eth_array = np.zeros((num_days, num_hours)) # clearing price in eth
    Price_kwh_eur_array = np.zeros((num_days, num_hours)) # clearing price in eur  
      
    #estimate the gas of the possible transaction based on sellers' offers and more
    #for i in range(len(gas_estimate)): # I need to do it for specific agent, hour and day of the year
    for day in range(num_days):
        for hour in range(num_hours):
    
            #complete the arrays with the values for:  buyer_bidQuantity, seller_bidQuantity, pros_dem_f
            #by calling function 
            buyer_bidQuantity, seller_bidQuantity, pros_dem_f = \
            initiate_Bids(day, hour, num_seller, num_buyer, pros_gen, battery_cap, pros_dem_ini, 
                          cons_dem, pros_dem_f, buyer_bidQuantity, seller_bidQuantity)
    
     
            # Then, the DSO/Operator realizes the negotiations and validation of the grid offline (Matlab or Python code)
            #Price_to_pay = 1*ether #comment this if you run it with matlab or pyhton
            ether = 10**18 # 1 ether = 1000000000000000000 wei
            ETH_2_EURO = 1612.9032 # equivalent eth to euro - 1 eth = 1612.9032 euro
            #p_bal = 0.00031 * ether # = 0.50 euro, in  wei
            #p_con = 0.00025 * ether # = 0.40 euro so that price in the range [0.10 , 0.90] euro, in wei
            p_bal_eur = 0.09
            p_bal = (p_bal_eur / ETH_2_EURO) * ether # = 0.50 euro, in  wei
            p_con_eur = 0.4 
            p_con = (p_con_eur / ETH_2_EURO) * ether # = 0.40 euro so that price in the range [0.10 , 0.90] euro, in wei
            minPrice_DSO_eur = 0.087 # euro/kWh - current tarrif in Greece for DSO buying energy from rooftop PV of up to 6 kW
            minPrice_DSO = (minPrice_DSO_eur / ETH_2_EURO) * ether # = 0.08 euro is the minimum price per kWh the DSO offers the sellers for their unmatched, in wei
            #minPrice_DSO = 0.000051 * ether # = 0.08 euro is the minimum price per kWh the DSO offers the sellers for their unmatched, in wei
            #conPayDSO_euro = 0.55 #0.55 euro - the price in euro per kWh the dso will offer consumers for their unmatched demand
            #conPay_dso = (conPayDSO_euro / ETH_2_EURO) * ether  #0.55 euro - the price per kWh the dso will offer consumers for their unmatched demand, in wei
            k = 3
            
            #Calculate price, R, ED and ES - by calling function 
            Price_kwh, R, R_array, ED_array, ES_array = \
                price_R(day, hour, num_buyer, num_seller, buyer_bidQuantity, seller_bidQuantity, ED_array, ES_array, 
                            battery_cap, R_array, p_bal, p_con, k, ETH_2_EURO, ether, minPrice_DSO)
                
            Price_kwh_array[day, hour] = Price_kwh 
            Price_kwh_eth = Price_kwh / 10**18 # price per kWh turned into eth from wei
            Price_kwh_eth_array[day, hour] = Price_kwh_eth
            Price_kwh_eur = Price_kwh_eth * ETH_2_EURO  # price per kWh turned into euro from eth
            Price_kwh_eur_array[day, hour] = Price_kwh_eur
            #print("Price to pay per kWh (Wei): {0}".format(Price_kwh))
            #print("Price to pay per kWh (ETH): {0}".format(Price_kwh_eth))
            #print("Price to pay per kWh (EURO): {0}\n".format(Price_kwh_eur))
             
            
            #find the available battery capacity for the auction / SOS: fix the batt use accordin to new code
            for agent_s in range(num_seller):
                
                if R <= 1: # so Demand <= Supply - this is CASE 2 from my notes
                    
                    sup_f = R * seller_bidQuantity[day, hour, agent_s]
                    noMat_s = seller_bidQuantity[day, hour, agent_s] - sup_f    
                    
                    if seller_battery[agent_s] == 1:
                        batt_curr_cap =  battery_cap[day, hour, agent_s] + (noMat_s * batt_ch_eff * batt_disch_eff)

                    #check if the batery of the seller has available capacity. 
                    #The extra is sold to the DSO with min price
                        if batt_curr_cap > battery_cap_max[agent_s]:

                            battery_cap[day, hour, agent_s] = battery_cap_max[agent_s] #if battery_cap is a 3D array 
                            
                        else: 
                            battery_cap[day, hour, agent_s] = batt_curr_cap
                             
                            
             
            
    #Price_kwh_eur_array is a 2D list containing the prices
    #it actually works correclty
    avePrice = np.mean(Price_kwh_eur_array) #average price of the whole year in euro
     
    #print("Function Average price: {:.2f}".format(avePrice))
    
    return avePrice



