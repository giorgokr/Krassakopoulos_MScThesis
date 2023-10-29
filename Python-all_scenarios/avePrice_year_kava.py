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
 
from Price_to_Pay_v5 import price
import random
from statistics import mean
#import matplotlib.pyplot as plt
#import numpy as np
 

def avePrice_0(num_days, num_hours, num_seller, num_buyer):
      
    # vector with sellers' bid quantities 
    seller_bidQuantity = [[[0 for _ in range(num_seller)] for _ in range(num_hours)] for _ in range(num_days)]
    # vector with sellers' initial own need in energy demand (before cover by his own gen) 
    pros_dem_ini = [[[random.uniform(0.5, 1.5) for _ in range(num_seller)] for _ in range(num_hours)] for _ in range(num_days)]
    # vector with sellers' own generation
    pros_gen = [[[random.uniform(1, 3) for _ in range(num_seller)] for _ in range(num_hours)] for _ in range(num_days)]
    # vector with sellers' final own need in energy demand (after cover by his own gen) 
    pros_dem_f = [[[0 for _ in range(num_seller)] for _ in range(num_hours)] for _ in range(num_days)]
    # vector with buyers' bid quantities (prosumers + consumers) 
    buyer_bidQuantity = [[[0 for _ in range(num_buyer+num_seller)] for _ in range(num_hours)] for _ in range(num_days)]
    # vector with consumers' demand  
    cons_dem = [[[random.uniform(0.5, 1.5) for _ in range(num_buyer)] for _ in range(num_hours)] for _ in range(num_days)]
    
    
    seller_battery = [random.randint(0 , 1) for _ in range(num_seller)] #generate randomly which sellers have batteries
    # denotes which sellers own batteries (1 owns battery - 0 no battery)
    bmax = [random.randint(5 , 10) for _ in range(num_seller)] 
    battery_cap_max = [x * y for x, y in zip(bmax, seller_battery)] # I should multiply each value with the respective seller_battery 
    #max capacity of sellers' batteries 
    battery_cap = [0 for _ in range(num_seller)] #includes the capacity of sellers' batteries - Initially they all have: 0 kWh
    # I should multiply each value with the respective seller_battery 
    
    
    ## Needed 2D arrays to save the ED, ES, R, and clearing prices in each auction
    #first index represents the day, second index represents the hour
    ED_array = [[0 for _ in range(num_hours)] for _ in range(num_days)] #initial demand in kWh
    ES_array = [[0 for _ in range(num_hours)] for _ in range(num_days)] #initial supply in kWh
    R_array = [[0 for _ in range(num_hours)] for _ in range(num_days)]
    Price_kwh_array = [[0 for _ in range(num_hours)] for _ in range(num_days)] # clearing price in wei
    Price_kwh_eth_array = [[0 for _ in range(num_hours)] for _ in range(num_days)] # clearing price in eth
    Price_kwh_eur_array = [[0 for _ in range(num_hours)] for _ in range(num_days)] # clearing price in eur  
    
    #estimate the gas of the possible transaction based on sellers' offers and more
    #for i in range(len(gas_estimate)): # I need to do it for specific agent, hour and day of the year
    for day in range(num_days):
        for hour in range(num_hours):
    
            # continue from here on 04/06/2023
            for agent_s in range(num_seller): #agent_s starts from index = 0 up to num_seller-1
                a = pros_gen[day][hour][agent_s]
                b = battery_cap[agent_s]  
                k = pros_dem_ini[day][hour][agent_s]
                pd = k - a - b 
                pros_dem_f[day][hour][agent_s] = max(pd, 0) 
                buyer_bidQuantity[day][hour][agent_s] = pros_dem_f[day][hour][agent_s] 
                sbQ = a + b - k # it has as zero only the ones who neither sell or buy  
                seller_bidQuantity[day][hour][agent_s] = max(sbQ, 0)
                
                
            # fill the buyer_bidQuantity array-list    
            i = 0
            for agent_b in range(num_seller, num_seller + num_buyer): 
                #agent_b values starting from "num_seller" up to "num_seller + num_buyer - 1"
                   
                buyer_bidQuantity[day][hour][agent_b] = cons_dem[day][hour][i]
    
                i += 1
    
    
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
               
            #I need to put a for loop here until the end of the code
            #the buyer_bidQuantity needs to become an 3-by-3 array with dimensions of (day - hour - buyer)
            
            ED = sum(buyer_bidQuantity[day][hour][agent_b] for agent_b in range(num_buyer+num_seller))  # total initial demand in kWh
            ED_array[day][hour] = ED #first index represents the day, second index represents the hour
            ES = sum(seller_bidQuantity[day][hour][agent_s] for agent_s in range(num_seller)) + \
                 sum(battery_cap[agent_s] for agent_s in range(num_seller)) # total forecatsted initial available supply in kWh + the 
                 #energy saved in batteries of sellers 
            ES_array[day][hour] = ES
            
            ###ERROR when supply is zero / fix it
            if ES != 0:
                R = ED/ES 
                R_array[day][hour] = R
            else:
                R = 10**-1000 #very small value to go close to 0, check paper 4 formula 6  
                R_array[day][hour] = R
                
            k = 3
            Price_kwh = int(price(p_bal, p_con, R, k, ETH_2_EURO, ether, minPrice_DSO)) # common price per kWh for all-function price from Price_to_Pay_v5.py file
            Price_kwh_array[day][hour] = Price_kwh 
            Price_kwh_eth = Price_kwh / 10**18 # price per kWh turned into eth from wei
            Price_kwh_eth_array[day][hour] = Price_kwh_eth
            Price_kwh_eur = Price_kwh_eth * ETH_2_EURO  # price per kWh turned into euro from eth
            Price_kwh_eur_array[day][hour] = Price_kwh_eur
            #print("Price to pay per kWh (Wei): {0}".format(Price_kwh))
            #print("Price to pay per kWh (ETH): {0}".format(Price_kwh_eth))
            #print("Price to pay per kWh (EURO): {0}\n".format(Price_kwh_eur))
            
            
            #find the available battery capacity for the auction / SOS: fix the batt use accordin to new code
            for agent_s in range(num_seller):
                
                if R <= 1: # so Demand <= Supply - this is CASE 2 from my notes
                    sup_f = R * seller_bidQuantity[day][hour][agent_s] #sup_f is the supply that will be sold to the consumers and not to the DSO
                    #supply_f[day][hour][agent_s] = sup_f
                    noMat_s = seller_bidQuantity[day][hour][agent_s] - sup_f # the unmatched supply of the seller with and without batt (with the amount sold to dso, if happened)
                    #noMatch_sup[day][hour][agent_s] = noMat_s
                    #the noMtach supply is sold to the grid (dso) 
                    
                    if seller_battery[agent_s] == 1:
                        batt_curr_cap =  battery_cap[agent_s] + noMat_s #current capacity of the batery / 
                    #check if the batery of the seller has available capacity. 
                    #The extra is sold to the DSO with min price
                        if batt_curr_cap > battery_cap_max[agent_s]:
                            battery_cap[agent_s] = battery_cap_max[agent_s]
                        else:
                            battery_cap[agent_s] = batt_curr_cap
                            
                            
            
            
    #Price_kwh_eur_array is a 2D list containing the prices
    #it actually works correclty
    avePrice = mean(hour for day in Price_kwh_eur_array for hour in day) #average price of the whole year in euro
     
    #print("Average price: {:.2f}".format(avePrice))
    
    return avePrice



