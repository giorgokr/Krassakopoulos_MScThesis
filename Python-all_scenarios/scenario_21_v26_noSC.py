#similar with file "SC_bids_pay_auto_v5" but here I implement the pricing function like in paper 4 more accuratly
#also in that one I implement several trades - like several auction rounds - let's say for 1 day, so 24 auctions
#this file is going with the .v3 version of the SC file
#I have the parts for the unmatched energy of the seller, including the case some of them have batteries

#this file goes along with the solidity SC file .v6
 
#SOS: this script includes also price bids from sellers and buyers but
#in the case of single price I don't want them to give prices as the price is decided bu the system
#So for the common for all price I need to remove the price bids from this file and the smart contract
#so the new file for this case will be the v8 py one and the v4 solidity one

#the python part uses kWh and euro while in solidity I send integers of (kWh * 10^6) and wei as it can't manage float numbers
#This code .v26_noSC is the same with .v25_noSC but the demand and generation data are the real ones and not random
   
import time 
from IPython import get_ipython #to read what I have imported by hand in the workspace before run the script
   
#from avePrice_year import avePrice_0 
#from function_findDemand import find_Demand
from function_irrad_to_power_pros40 import energy_offer
from function_initiateBids import initiate_Bids
from function_priceR import price_R
from function_EMA import find_EMA
#import random 
#import matplotlib.pyplot as plt
import numpy as np
 
# Start the timer
start_time = time.time() 

#ether = 10**18 # 1 ether = 1000000000000000000 wei
  
# Number of days in a year
num_days = 365
# Number of hours in a day
num_hours = 24
num_seller = 40 # declare the number of sellers
num_buyer = 99 - num_seller # declare the number of buyers


#where at the 3x3 arrays as lists below the 
#first index represents the day, 
#the second index represents the hour, and 
#the third index represents the agent (seller or buyer).

# vector with sellers' bid quantities 
seller_bidQuantity = np.zeros((num_days, num_hours, num_seller))

 
#import array containing the total hourly demand of prosumers and consumers
#demand_hourly_total = find_Demand(num_days, num_hours, num_seller, num_buyer) #using the function, takes 25 secs
  
# Get the IPython console instance - when I import "demand_hourly_total_for99Houses" in workspace by hand 
ipython = get_ipython()
demand_hourly_total = ipython.user_ns['demand_hourly_total_for99Houses'] 

# vector with sellers' initial own need in energy demand (before cover by his own gen) 
pros_dem_ini = np.zeros((num_days, num_hours, num_seller)) 
pros_dem_ini[:, :, :num_seller] = demand_hourly_total[:, :, :num_seller]

###############    
# vector with sellers' own generation 

#number of panels (modules) every prosumers owns -> for now its random values / 
#number of panels determines the prosumers capacity in kWh
    
panels_num = np.array([5, 10, 5, 5, 10, 5, 5, 25, 10, 5, 5, 5, 15, 5, 10,\
                       10, 5, 10, 10, 25, 5, 10, 5, 10, 5, 10, 10, 15, 5, 5,\
                       5, 25, 10, 10, 5, 10, 15, 5, 5, 5]) # number of panels each prosumer has - they denote also his PV capacity
pros_gen, E_panel_Archal, E_panel_Archanes, E_panel_Her, E_panel_NArvi = energy_offer(num_days, num_hours, num_seller, panels_num) # input pros generated energy from the function
 
#for when I do not generate it by function, but I import the data by hand in the workspace
"""
pros_gen = energy_gen
E_panel_Archal = E_gen_Archal
E_panel_Archanes = E_gen_Archanes 
E_panel_Her = E_gen_Her
E_panel_NArvi = E_gen_NArvi   
"""

# vector with sellers' final own need in energy demand (after cover by his own gen) 
pros_dem_f = np.zeros((num_days, num_hours, num_seller)) 
# vector with buyers' bid quantities (prosumers + consumers) 
buyer_bidQuantity = np.zeros((num_days, num_hours, num_buyer+num_seller)) 
# vector with consumers' demand  
cons_dem = np.zeros((num_days, num_hours, num_buyer))
cons_dem[:, :, :num_buyer] = demand_hourly_total[:, :, num_seller:]


################    
#About batteries  
 
#seller_battery = np.full(num_seller, 1) # all sellers have batts - num_seller is the length (columns) of the array and 1 is the value in each
seller_battery = np.full(num_seller, 0) # no sellers have batts
 
# denotes which sellers own batteries (1 owns battery - 0 no battery) 
 
 
#max capacity of sellers' batteries
bmax = np.full(num_seller, 5) 
  
SOC_80 = 0.8 # factor for max SOC to be 80%  
SOC_20 = 0.2 # factor for min SOC to be 20%  
battery_cap_max = SOC_80 * np.multiply(bmax, seller_battery) #max charge level (SOC) that we allow the batteries to be
battery_cap_min = SOC_20 * np.multiply(bmax, seller_battery) #max charge level (SOC) that we allow the batteries to be
battery_cap = np.full(num_seller, 0) 
battery_cap = battery_cap_min * np.ones((num_days, num_hours, num_seller))
# I should multiply each value with the respective seller_battery 


## Needed 2D arrays to save the ED, ES, R, and clearing prices in each auction
#first index represents the day, second index represents the hour
ED_array = np.zeros((num_days, num_hours)) #initial demand in kWh
ES_array = np.zeros((num_days, num_hours)) #initial supply in kWh
demand_F_array = np.zeros((num_days, num_hours)) #final demand in kWh by consum to prosum only
supply_F_array = np.zeros((num_days, num_hours)) #final supply in kWh by prosum to consum only
final_dem_ar = np.zeros((num_days, num_hours)) #total final demand for this auction round by consumers to prosum and dso
final_sup_ar = np.zeros((num_days, num_hours)) #total final supply for this auction round by prosumers to cons and dso
R_array = np.zeros((num_days, num_hours)) 
Price_kwh_array = np.zeros((num_days, num_hours)) # clearing price in wei
Price_kwh_eth_array = np.zeros((num_days, num_hours)) # clearing price in eth
Price_kwh_eur_array = np.zeros((num_days, num_hours)) # clearing price in eur   
Price_EMA = np.zeros((num_days, num_hours)) # array keeping the EMA prices in euro
  
###### Arrays 3D needed for the matching between supply and demand
supply_f = np.zeros((num_days, num_hours, num_seller)) #final energy quantity each seller will provide tot he consumers (not the DSO)
noMatch_sup = np.zeros((num_days, num_hours, num_seller)) #total no matched supply of seller i, with peers and dso involved
total_supply = np.zeros((num_days, num_hours, num_seller)) # total energy (supply) sold (induced to the grid - peers and dso) by the prosumers 
receive_pr = np.zeros((num_days, num_hours, num_seller)) #array with the final price each seller will receive in wei from peers
receive_pr_eth = np.zeros((num_days, num_hours, num_seller)) #array with the final price each seller will receive in eth from peers
receive_pr_eur = np.zeros((num_days, num_hours, num_seller)) #array with the final price each seller will receive in euro from peers
receive_dso = np.zeros((num_days, num_hours, num_seller)) #array with the final price each seller will receive in wei from dso
receive_dso_eth = np.zeros((num_days, num_hours, num_seller)) #array with the final price each seller will receive in eth from dso
receive_dso_eur = np.zeros((num_days, num_hours, num_seller)) #array with the final price each seller will receive in euro from dso
tot_receive = np.zeros((num_days, num_hours, num_seller)) #total price received in wei: money prosumers get from peers and dso 
tot_receive_eth = np.zeros((num_days, num_hours, num_seller)) #total price received in eth: money prosumers get from peers and dso
tot_receive_eur = np.zeros((num_days, num_hours, num_seller)) #total price received in euro: money prosumers get from peers and dso
       
demand_f = np.zeros((num_days, num_hours, num_buyer+num_seller)) #final energy quantity each consumer will buy
demand_dso = np.zeros((num_days, num_hours, num_buyer+num_seller)) #demand that will be covered by dso
total_demand = np.zeros((num_days, num_hours, num_buyer+num_seller)) # total energy (demand) bought (by the grid - peers and dso) by the consumers 
pay_pr = np.zeros((num_days, num_hours, num_buyer+num_seller)) #array with the final price each buyer will pay in wei the prosumers
pay_pr_eth = np.zeros((num_days, num_hours, num_buyer+num_seller)) #array with the final price each buyer will pay in eth the prosumers
pay_pr_eur = np.zeros((num_days, num_hours, num_buyer+num_seller)) #array with the final price each buyer will pay in euro the prosumers
pay_dso = np.zeros((num_days, num_hours, num_buyer+num_seller)) #array with the final price each buyer will pay in wei the dso
pay_dso_eth = np.zeros((num_days, num_hours, num_buyer+num_seller)) #array with the final price each buyer will pay in eth the dso
pay_dso_eur = np.zeros((num_days, num_hours, num_buyer+num_seller)) #array with the final price each buyer will pay in euro the dso
total_pay = np.zeros((num_days, num_hours, num_buyer+num_seller)) #array with the final price each buyer will pay in wei the prosum and dso
total_pay_eth = np.zeros((num_days, num_hours, num_buyer+num_seller)) #array with the final price each buyer will pay in eth the prosum and dso
total_pay_eur = np.zeros((num_days, num_hours, num_buyer+num_seller)) #array with the final price each buyer will pay in euro the prosum and dso
  
   
batt_ch_eff = 0.95 # charging efficiency of batteries
batt_disch_eff = 0.9 # discharging efficiency of batteries
##################
######The trading procedure for every hour of every day of 1 year starts here:    
 
bb = np.ones((num_days, num_hours, num_seller))    
    
for day in range(num_days):
    for hour in range(num_hours):
        
        #complete the arrays with the values for:  buyer_bidQuantity, seller_bidQuantity, pros_dem_f
        #by calling function 
        buyer_bidQuantity, seller_bidQuantity, pros_dem_f, bb = \
        initiate_Bids(bb, day, hour, num_seller, num_buyer, pros_gen, battery_cap, battery_cap_min, pros_dem_ini, 
                      cons_dem, pros_dem_f, buyer_bidQuantity, seller_bidQuantity)  
        
     
        #print("ok - DSO retrieved the seller's and the buyer's bids \n")
        #print("Auctions for DAY {0} and HOUR {1} can start \n".format(day+1, hour+1))


        # Then, the DSO/Operator realizes the negotiations and validation of the grid offline (Matlab or Python code)
        #Price_to_pay = 1*ether #comment this if you run it with matlab or pyhton
        ether = 10**18 # 1 ether = 1000000000000000000 wei
        ETH_2_EURO = 1612.9032 # equivalent eth to euro - 1 eth = 1612.9032 euro
        p_bal_eur = 0.095 # euro/kWh 
        p_bal = (p_bal_eur / ETH_2_EURO) * ether # the above euro in  wei
        conPayDSO_euro = 0.155 #the price in euro per kWh the dso will offer consumers for their unmatched demand - the normal price their retail utility asks per kWh
        conPay_dso = (conPayDSO_euro / ETH_2_EURO) * ether  #the price per kWh the dso will offer consumers for their unmatched demand, in wei
        minPrice_DSO_eur = 0.087 # euro/kWh - current tarrif in Greece for DSO buying energy from rooftop PV of up to 6 kW
        minPrice_DSO = (minPrice_DSO_eur / ETH_2_EURO) * ether # = 0.08 euro is the minimum price per kWh the DSO offers the sellers for their unmatched, in wei
        conPayDSO_MAX_euro = conPayDSO_euro #the max price the retail utility may ask per kWh
        #conPayDSO_MAX_euro = 0.5
        conPay_dso_MAX = (conPayDSO_MAX_euro / ETH_2_EURO) * ether 
        p_con_eur = conPayDSO_MAX_euro - p_bal_eur # 0.4 # euro/kWh - so the max price by the LEM cannot overpass the price asked by retail utilities 
        # so that price_max = p_bal_eur + p_con_eur
        p_con = (p_con_eur / ETH_2_EURO) * ether # so that price in the range, in wei
             
        k = 3 # initial value - mama
          
            
        #Calculate price, R, ED and ES - by calling function 
        Price_kwh, R, R_array, ED_array, ES_array = \
            price_R(day, hour, num_buyer, num_seller, buyer_bidQuantity, seller_bidQuantity, ED_array, ES_array, 
                        battery_cap, battery_cap_min, R_array, p_bal, p_con, k, ETH_2_EURO, ether, minPrice_DSO)
              
        Price_kwh_array[day, hour] = Price_kwh 
        Price_kwh_eth = Price_kwh / 10**18 # price per kWh turned into eth from wei
        Price_kwh_eth_array[day, hour] = Price_kwh_eth
        Price_kwh_eur = Price_kwh_eth * ETH_2_EURO  # price per kWh turned into euro from eth
        Price_kwh_eur_array[day, hour] = Price_kwh_eur
        #print("Price to pay per kWh (Wei): {0}".format(Price_kwh))
        #print("Price to pay per kWh (ETH): {0}".format(Price_kwh_eth))
        #print("Price to pay per kWh (EURO): {0}\n".format(Price_kwh_eur))
         
  
        #####
          
        # calculate and keep record of the EMA prices, to use in the auctions
        Price_EMA, Aver_Price00 = find_EMA(day, hour, num_days, num_hours, num_buyer, num_seller, Price_EMA, 
                    Price_kwh_eur_array, batt_ch_eff, batt_disch_eff)
              
        #find the final amount of energy actually sold and bought by each prosumer (seller)
        for agent_s in range(num_seller):
            
            battery_cap[day, hour, agent_s] = bb[day, hour, agent_s] + battery_cap_min[agent_s]
            
            #for prosumers who sell 
            if seller_bidQuantity[day, hour, agent_s] > 0 :
                if R <= 1: # so Demand <= Supply
                    #for prosumers who sell   
                    supply_f[day, hour, agent_s] = R * seller_bidQuantity[day, hour, agent_s] #sup_f is the supply that will be sold to the consumers and not to the DSO
                    noMatch_sup[day, hour, agent_s] = seller_bidQuantity[day, hour, agent_s] - supply_f[day, hour, agent_s] # the unmatched supply of the seller with and without batt (with the amount sold to dso, if happened)
                    #the noMtach supply is sold to the grid (dso)  
                       
                    if seller_battery[agent_s] == 1:
                        #battery_on = seller_battery[agent_s] # 1 if the seller has batteries and wants to keep the energy to sell it in a later auction
                    #battery_on = 0 if the seller wants to sell his unmatched energy to the DSO for a min price in this auction
                       
                        #batt_curr_cap =  battery_cap[agent_s] + (noMatch_sup[day, hour, agent_s] * batt_ch_eff * batt_disch_eff) # use round trip charging and discharging eff here - current capacity of the batery
                        batt_curr_cap =  battery_cap[day, hour, agent_s] + (noMatch_sup[day, hour, agent_s] * batt_ch_eff * batt_disch_eff) #if battery_cap is a 3D array  
                    #check if the batery of the seller has available capacity. The extra is sold to the DSO with min price
                        if batt_curr_cap > battery_cap_max[agent_s]: #battery_cap_max includes the SOC_80 max charge factor
                            battery_cap[day, hour, agent_s] = battery_cap_max[agent_s] #if battery_cap is a 3D array 
                            noMat_s = (battery_cap[day, hour, agent_s] + noMatch_sup[day, hour, agent_s]) - battery_cap_max[agent_s] #if battery_cap is a 3D array 
                            noMatch_sup[day, hour, agent_s] = noMat_s  
                        else:     
                            battery_cap[day, hour, agent_s] = batt_curr_cap #if battery_cap is a 3D array 
                            noMatch_sup[day, hour, agent_s] = 0
                            #noMatch_sup[day, hour, agent_s] = noMat_s  
                          
                         
                else: # R > 1 or so Demand > Supply
                
                    Pdeg = 0.042 # 0.042 eur/kWh - degradation cost per kWh of using the batt
                    #Ebatt_dis = battery_cap[agent_s]  
                    # so that Ebatt_dis cannot be lower that the SOC-20 of the battery of this prosumer
                    Ebatt_dis = battery_cap[day, hour, agent_s] - battery_cap_min[agent_s] #if battery_cap is a 3D array
                    #Ebatt_dis = battery_cap[day, hour, agent_s]  #if battery_cap is a 3D array
                          
                    # profit in euro by the selling of the energy saved in battery based in current auction price
                    Pr_batt_now = (Price_kwh_eur_array[day, hour] - Pdeg) * Ebatt_dis 
                     
                    # profit in euro by the selling of the energy saved in battery based in EMA of previous 24 auction prices
                    Pr_batt_EMA = (Price_EMA[day, hour] - Pdeg) * Ebatt_dis
                           
                    #price the consumer would pay if buy that energy from the grid
                    #Pr_grid = Ebatt_dis *  conPayDSO_euro
                    
                    # Do comparisons and decide if use the batt or not
                    if Pr_batt_now > Pr_batt_EMA: #if current price is higher than EMA, then sell the battery up to its SOC-20
                         
                        supply_f[day, hour, agent_s] = seller_bidQuantity[day, hour, agent_s] + Ebatt_dis #if battery_cap is a 3D array
                        
                        #discharge the battery of the energy it exported
                        batt_cap_now = battery_cap[day, hour, agent_s]
                        battery_cap[day, hour, agent_s] = batt_cap_now - Ebatt_dis  
                        
                        noMatch_sup[day, hour, agent_s] = 0
                         
                    else: #if current price is lower or equal than EMA, then do not sell the battery
                        supply_f[day, hour, agent_s] = seller_bidQuantity[day, hour, agent_s] 
                         
                        noMatch_sup[day, hour, agent_s] = 0
                         
                total_supply[day, hour, agent_s] = supply_f[day, hour, agent_s] + noMatch_sup[day, hour, agent_s] # total energy sold (induced to the grid - peers and dso) by the prosumers
                
                # compute the final price each seller will receive
                receive_pr[day, hour, agent_s] = supply_f[day, hour, agent_s] * Price_kwh #total price in wei: money prosumers get from peers  
                receive_dso[day, hour, agent_s] = noMatch_sup[day, hour, agent_s] * minPrice_DSO  #total price in wei: money prosumers get from DSO  
                receive_pr_eth[day, hour, agent_s] = receive_pr[day, hour, agent_s] / 10**18 #total price in eth from peers
                receive_dso_eth[day, hour, agent_s] = receive_dso[day, hour, agent_s] / 10**18 #total price in eth from dso
                receive_pr_eur[day, hour, agent_s] = receive_pr_eth[day, hour, agent_s] * ETH_2_EURO #total price in euro from peers
                receive_dso_eur[day, hour, agent_s] = receive_dso_eth[day, hour, agent_s] * ETH_2_EURO #total price in euro from dso
                
                #received money from DSO and consumers summed          
                tot_receive[day, hour, agent_s] = receive_pr[day, hour, agent_s] +  receive_dso[day, hour, agent_s]  #total price received in wei: money prosumers get from peers and dso 
                tot_receive_eth[day, hour, agent_s] = receive_pr_eth[day, hour, agent_s] + receive_dso_eth[day, hour, agent_s] #total price received in eth: money prosumers get from peers and dso
                tot_receive_eur[day, hour, agent_s] = receive_pr_eur[day, hour, agent_s] + receive_dso_eur[day, hour, agent_s] #total price received in euro: money prosumers get from peers and dso
                  
                #print("Seller {0} has no matched supply of {1} kWh".format(agent_s+1, noMat_s))
                #print("Prosumer {0} will total sell {1} kWh and total receive {2} ETH or {3} EURO\n".format(agent_s+1, tot_sup, tot_rec_eth, tot_rec_eur))
                 
                 
            #for prosumers who buy
            if seller_bidQuantity[day, hour, agent_s] == 0:
                if R <= 1: # so Demand <= Supply 
                    demand_f[day, hour, agent_s] = buyer_bidQuantity[day, hour, agent_s]  
                    
                    demand_dso[day, hour, agent_s] = 0 #demand that will be covered by dso

                else: # R > 1 or Demand > Supply
                    demand_f[day, hour, agent_s] = buyer_bidQuantity[day, hour, agent_s] / R #demand of prosumer that will be covered by other prosumers
                    
                    demand_dso[day, hour, agent_s] = buyer_bidQuantity[day, hour, agent_s] - demand_f[day, hour, agent_s] #demand that will be covered by dso
               
                total_demand[day, hour, agent_s] = demand_f[day, hour, agent_s] + demand_dso[day, hour, agent_s] #total demand by prossumer x of this round that will be covered by prosum and dso
                
                # compute the final price each prosumer who needs to buy in this round will pay
                pay_pr[day, hour, agent_s] = demand_f[day, hour, agent_s] * Price_kwh
                pay_dso[day, hour, agent_s] = demand_dso[day, hour, agent_s] * conPay_dso #total price in wei - money pros pay to dso
                pay_pr_eth[day, hour, agent_s] = pay_pr[day, hour, agent_s] / 10**18 #total price in eth - money pros pay to prosum  
                pay_dso_eth[day, hour, agent_s] =  pay_dso[day, hour, agent_s] / 10**18 #total price in eth - money pros pay to dso
                pay_pr_eur[day, hour, agent_s] = pay_pr_eth[day, hour, agent_s] * ETH_2_EURO #total price in euro - money pros pay to prosum 
                pay_dso_eur[day, hour, agent_s] = pay_dso_eth[day, hour, agent_s] * ETH_2_EURO #total price in euro - money pros pay to dso
                
                #total prices paid to DSO and consumers summed
                total_pay[day, hour, agent_s] = pay_pr[day, hour, agent_s] + pay_dso[day, hour, agent_s] #total price in wei - money cons pay to prosum and dso
                total_pay_eth[day, hour, agent_s] =  pay_pr_eth[day, hour, agent_s] + pay_dso_eth[day, hour, agent_s] #total price in eth - money cons pay to prosum and dso
                total_pay_eur[day, hour, agent_s] = pay_pr_eur[day, hour, agent_s] + pay_dso_eur[day, hour, agent_s] #total price in eur - money cons pay to prosum and dso
                  
                #print("Prosumer {0} will buy {1} kWh and total pay {2} ETH or {3} EURO\n".format(agent_s+1, tot_dem, tot_pay_eth, tot_pay_eur))

    
        #stayed here - 04/06/2023 - at the following you need to fix the indexes in the arrays to search after
        #the prosumers who have already been placed in their cells - what about prosumers who are 0 demand and supply?
        
        #find the final amount of energy actually bought (demand) by each consumer (buyer)
        
        for agent_b in range(num_seller, num_buyer+num_seller):
            #dem_f is the demand that will be covered by the available supply of the prosumers
            if R <= 1: # so Demand <= Supply 
                demand_f[day, hour, agent_b] = buyer_bidQuantity[day, hour, agent_b]
                
                demand_dso[day, hour, agent_b] = 0 #demand that will be covered by dso
                 
            else: # in this case, R>1, so buyer_bidQuantity > Supply / # so Demand > Supply 
                demand_f[day, hour, agent_b] = buyer_bidQuantity[day, hour, agent_b] / R #demand that will be covered by prosumers
                
                demand_dso[day, hour, agent_b] = buyer_bidQuantity[day, hour, agent_b] - demand_f[day, hour, agent_b] #demand that will be covered by dso
                
                  
            tot_dem = demand_f[day, hour, agent_b] + demand_dso[day, hour, agent_b] #total demand by consumer x of this round that will be covered by prosum and dso
            
                   
            # compute the final price each buyer will pay
            pay_pr[day, hour, agent_b] = demand_f[day, hour, agent_b] * Price_kwh #total price in wei - money cons pay to prosum  
            pay_dso[day, hour, agent_b] = demand_dso[day, hour, agent_b] * conPay_dso #total price in wei - money cons pay to dso
            pay_pr_eth[day, hour, agent_b] = pay_pr[day, hour, agent_b] / 10**18 #total price in eth - money cons pay to prosum 
            pay_dso_eth[day, hour, agent_b] = pay_dso[day, hour, agent_b] / 10**18 #total price in eth - money cons pay to dso
            pay_pr_eur[day, hour, agent_b] = pay_pr_eth[day, hour, agent_b] * ETH_2_EURO #total price in euro - money cons pay to prosum 
            pay_dso_eur[day, hour, agent_b] = pay_dso_eth[day, hour, agent_b] * ETH_2_EURO #total price in euro - money cons pay to dso
            
            #total prices paid to DSO and consumers summed   
            total_pay[day, hour, agent_b] = pay_pr[day, hour, agent_b] + pay_dso[day, hour, agent_b] #total price in wei - money cons pay to prosum and dso 
            total_pay_eth[day, hour, agent_b] = pay_pr_eth[day, hour, agent_b] + pay_dso_eth[day, hour, agent_b] #total price in eth - money cons pay to prosum and dso   
            total_pay_eur[day, hour, agent_b] = pay_pr_eur[day, hour, agent_b] + pay_dso_eur[day, hour, agent_b] #total price in eur - money cons pay to prosum and dso
            
            #print("Consumer {0} will buy {1} kWh and total pay {2} ETH or {3} EURO\n".format(agent_b + 1 - num_seller, tot_dem, tot_pay_eth, tot_pay_eur))

 
        # chech if the matching is correct by looking at the condition: total_supply = total_demand
        #prosum_sup = sum(supply_f[day][hour][agent_s] for agent_s in range(num_seller)) #total final supply by prosumers to cons
        supply_F_array[day, hour] = np.sum(supply_f[day, hour, :num_seller]) #total final supply by prosumers to cons 
        
        #consum_demand = sum(demand_f[day][hour][agent_b] for agent_b in range(num_buyer+num_seller)) #total final demand by consumers and pros to prosum
        demand_F_array[day, hour] = np.sum(demand_f[day, hour, :num_buyer+num_seller]) #total final demand by consumers and pros to prosum
          
        initial_supply = ES_array[day, hour] #total initial supply
        initial_demand = ED_array[day, hour] #total initial demand
         
        #final_sup = sum(total_supply[day][hour][agent_s] for agent_s in range(num_seller)) #total final supply for this auction round by prosumers to cons and dso
        final_sup_ar[day, hour] = np.sum(total_supply[day, hour, :num_seller]) #total final supply for this auction round by prosumers to cons and dso
         
        #final_dem = sum(total_demand[day][hour][agent_b] for agent_b in range(num_buyer+num_seller)) #total final demand for this auction round by consumers and pros to prosum and dso
        final_dem_ar[day, hour] = np.sum(total_demand[day, hour, :num_buyer+num_seller]) #total final demand for this auction round by consumers and pros to prosum and dso
         
        #if total_supply == total_demand: print("Matching between peers ONLY is correct, Supply = Demand") 
        #else: print("Matching between peers ONLY is NOT correct, Supply different than Demand")
        """
        print("Total initial supply: {0} kWh".format(initial_supply))
        print("Total initial demand: {0} kWh \n".format(initial_demand))
        print("Total final supply (to consum + pros only): {0} kWh".format(supply_F_array[day, hour]))
        print("Total final demand (covered by prosum only): {0} kWh\n".format(demand_F_array[day, hour]))
        print("Total final supply (to consum, pros + dso): {0} kWh".format(final_sup_ar[day, hour])
        print("Total final demand (covered by prosum + dso): {0} kWh\n".format(final_dem_ar[day, hour]))
        """

         
        #print("Auction round of hour X of day Y is over")
        print("Auctions for DAY {0} and HOUR {1} are over. \n".format(day+1, hour+1))
 
    
    
print("Prosumers number: {0}".format(num_seller))
print("Consumers number: {0}".format(num_buyer))
#calculate the average price per kWh for the whole period of the auctions
avePrice = np.mean(Price_kwh_eur_array) #average price of the whole period (days and hours) in euro 
print("Average price: {:.4f} EURO \n".format(avePrice))
 
     
# End the timer
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time    

# Print the elapsed time
print("Elapsed time: {:.2f} seconds".format(elapsed_time))   
 







