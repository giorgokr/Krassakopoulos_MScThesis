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
#This code .v22_noSC is the same with v21_help but I do not call the SC to see if I can save time
   
import time 
#import json
#import pprint
#from web3 import Web3
from Price_to_Pay_v5 import price

"""
from prosum_receive import pros_rec #plot function
from seller_bid import seller_bid #plot function
from consum_pay import consum_pay #plot function
from buyer_bid import buyer_bid #plot function
from price_common import price_common #plot function
from R_ratio import R_ratio #plot function
from price_R import price_R #plot function
from supply_final import supply_final #plot function
from demand_final import demand_final #plot function
"""

from avePrice_year import avePrice_0 
#import random
#import matplotlib.pyplot as plt
import numpy as np

# Start the timer
start_time = time.time() 

#ether = 10**18 # 1 ether = 1000000000000000000 wei
  
# Number of days in a year
num_days = 1
# Number of hours in a day
num_hours = 24
num_seller = 4 # declare the number of sellers
num_buyer = 4 # declare the number of buyers
 
#the following vectors need to become more cleverly denoted
#vectors with bids and offers from buyers and sellers
gas_estimate = np.zeros((num_days, num_hours, num_seller)) 


#where at the 3x3 arrays as lists below the 
#first index represents the day, 
#the second index represents the hour, and 
#the third index represents the agent (seller or buyer).
     
# vector with sellers' bid quantities 
seller_bidQuantity = np.zeros((num_days, num_hours, num_seller))
# vector with sellers' initial own need in energy demand (before cover by his own gen) 
pros_dem_ini = np.random.uniform(0.5, 1.6, size=(num_days, num_hours, num_seller)) 
   
# vector with sellers' own generation 
#with the following I have them generate only between 6am and 6pm
"""
pros_gen = np.zeros((num_days, num_hours, num_seller)) 
for hour in range(num_hours):
    if (18 < hour <= 23) or (0 <= hour < 6):
        pros_gen[0, hour, 0] = 0
    else:
        pros_gen[0, hour, 0] = np.random.uniform(1, 3)    
"""
#if gen increases, available energy to sell in each auction also increases and so the price falls
pros_gen = np.random.uniform(1, 3, size=(num_days, num_hours, num_seller))
#pros_gen = np.random.uniform(1, 3, size=(num_days, num_hours, num_seller))
 
# vector with sellers' final own need in energy demand (after cover by his own gen) 
pros_dem_f = np.zeros((num_days, num_hours, num_seller)) 
# vector with buyers' bid quantities (prosumers + consumers) 
buyer_bidQuantity = np.zeros((num_days, num_hours, num_buyer+num_seller)) 
# vector with consumers' demand  
cons_dem = np.random.uniform(0.5, 1.6, size=(num_days, num_hours, num_buyer))
# vector with sellers' bid weights 
seller_bidWeight = np.ones((num_days, num_hours, num_seller))
# vector with buyers' bid weights 
buyer_bidWeight = np.ones((num_days, num_hours, num_buyer))
   
agent_type = [0, 1] #(0 for seller, 1 for buyer) - declared as a list
#agent_type = np.array([0, 1]) #(0 for seller, 1 for buyer) - declared as a numpy array
  
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
     
""" 
#these arrays were covered after calling the SC
## Needed arrays for when the Operator/DSO retrieves the bids 
seller_Data = np.zeros((num_days, num_hours, num_seller), dtype = object)
seller_bal = np.zeros((num_days, num_hours, num_seller))
seller_bal_eth = np.zeros((num_days, num_hours, num_seller))
seller_en_bal = np.zeros((num_days, num_hours, num_seller))
seller_en_bal_eth = np.zeros((num_days, num_hours, num_seller))
seller_real_bal = np.zeros((num_days, num_hours, num_seller))
seller_real_bal_eth = np.zeros((num_days, num_hours, num_seller))
  
buyer_Data = np.zeros((num_days, num_hours, num_seller), dtype = object) 
buyer_bal = np.zeros((num_days, num_hours, num_seller))
buyer_bal_eth = np.zeros((num_days, num_hours, num_seller))
buyer_en_bal = np.zeros((num_days, num_hours, num_seller))
buyer_en_bal_eth = np.zeros((num_days, num_hours, num_seller))
buyer_real_bal = np.zeros((num_days, num_hours, num_seller))
buyer_real_bal_eth = np.zeros((num_days, num_hours, num_seller))
"""
 
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
 
    
#estimate the gas of the possible transaction based on sellers' offers and more
#for i in range(len(gas_estimate)): # I need to do it for specific agent, hour and day of the year
for day in range(num_days):
    for hour in range(num_hours):
    
        # continue from here on 04/06/2023
        for agent_s in range(num_seller): #agent_s starts from index = 0 up to num_seller-1
            a = pros_gen[day, hour, agent_s]
            #b = battery_cap[agent_s]   
            b = battery_cap[day, hour, agent_s] #if batery_cap is a 3D array  
            k = pros_dem_ini[day, hour, agent_s]
            pd = k - a - b   
            pros_dem_f[day, hour, agent_s] = max(pd, 0) 
            buyer_bidQuantity[day, hour, agent_s] = pros_dem_f[day, hour, agent_s] 
            sbQ = a + b - k # it has as zero only the ones who neither sell or buy  
            seller_bidQuantity[day, hour, agent_s] = max(sbQ, 0)
            
                 
        # fill the buyer_bidQuantity array-list with the consumers    
        i = 0
        for agent_b in range(num_seller, num_seller + num_buyer): 
            #agent_b values starting from "num_seller" up to "num_seller + num_buyer - 1"
               
            buyer_bidQuantity[day, hour, agent_b] = cons_dem[day, hour, i] 

            i += 1
    
        #print("ok - DSO retrieved the seller's and the buyer's bids \n")
        #print("Auctions for DAY {0} and HOUR {1} can start \n".format(day+1, hour+1))


        # Then, the DSO/Operator realizes the negotiations and validation of the grid offline (Matlab or Python code)
        #Price_to_pay = 1*ether #comment this if you run it with matlab or pyhton
        ether = 10**18 # 1 ether = 1000000000000000000 wei
        ETH_2_EURO = 1612.9032 # equivalent eth to euro - 1 eth = 1612.9032 euro
        p_bal = 0.00031 * ether # = 0.50 euro, in  wei
        p_con = 0.00025 * ether # = 0.40 euro so that price in the range [0.10 , 0.90] euro, in wei
        minPrice_DSO = 0.000051 * ether # = 0.08 euro is the minimum price per kWh the DSO offers the sellers for their unmatched, in wei
        conPayDSO_euro = 0.55 #0.55 euro - the price in euro per kWh the dso will offer consumers for their unmatched demand
        conPay_dso = (conPayDSO_euro / ETH_2_EURO) * ether  #0.55 euro - the price per kWh the dso will offer consumers for their unmatched demand, in wei
          
        #I need to put a for loop here until the end of the code
        #the buyer_bidQuantity needs to become an 3-by-3 array with dimensions of (day - hour - buyer)
        
        #ED = sum(buyer_bidQuantity[day][hour][agent_b] for agent_b in range(num_buyer+num_seller))  # total initial demand in kWh
        ED = np.sum(buyer_bidQuantity[day, hour, :num_buyer+num_seller]) # total initial demand in kWh
        ED_array[day, hour] = ED #first index represents the day, second index represents the hour
        #ES = sum(seller_bidQuantity[day][hour][agent_s] for agent_s in range(num_seller)) + \
         #    sum(battery_cap[agent_s] for agent_s in range(num_seller)) # total forecatsted initial available supply in kWh + the 
             #energy saved in batteries of sellers 
        #ES = np.sum(seller_bidQuantity[day, hour, :num_seller]) + np.sum(battery_cap[:num_seller]) # total forecatsted 
        ES = np.sum(seller_bidQuantity[day, hour, :num_seller]) + np.sum(battery_cap[day, hour, :num_seller]) #if batery_cap is a 3D array
        #initial available supply in kWh + the energy saved in batteries of sellers     
        ES_array[day, hour] = ES 
        
        ###ERROR when supply is zero / fix it
        if ES != 0:
            R = ED/ES 
            R_array[day, hour] = R
        else:
            R = 10**-1000 #very small value to go close to 0, check paper 4 formula 6  
            R_array[day, hour] = R
            
        k = 3
        Price_kwh = int(price(p_bal, p_con, R, k)) # common price per kWh for all-function price from Price_to_Pay_v5.py file
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
        time_periods = 24 # number of hours the EMA includes
        mult = 2 / (time_periods + 1) # the weighting multiplier we use in the EMA
        #price used for EMA calc when hour=0 and day = 0
        Price_ave0 = avePrice_0(num_days, num_hours, num_seller, num_buyer) 
        if day == 0 and hour == 0:  
            Price_EMA[day, hour] = (Price_kwh_eur_array[day, hour] * mult) + (Price_ave0 * (1-mult))
        else: #for the very first time, when hour = 0 and I do not have previous data
            Price_EMA[day, hour] = (Price_kwh_eur_array[day, hour] * mult) + (Price_EMA[day, hour-1] * (1-mult))
         
            #in different file feed it with the prices for one year based only in supply and demand
            #from these calculate only SMA or EMA and use it as the yesterday EMA for the hour = 0 case 
             
        #find the final amount of energy actually sold and bought by each prosumer (seller)
        for agent_s in range(num_seller):
             
            #for prosumers who sell 
            if seller_bidQuantity[day, hour, agent_s] > 0 :
                if R <= 1: # so Demand <= Supply
                    #for prosumers who sell   
                    #sup_f = R * seller_bidQuantity[day, hour, agent_s] #sup_f is the supply that will be sold to the consumers and not to the DSO
                    supply_f[day, hour, agent_s] = R * seller_bidQuantity[day, hour, agent_s]
                    noMatch_sup[day, hour, agent_s] = seller_bidQuantity[day, hour, agent_s] - supply_f[day, hour, agent_s] # the unmatched supply of the seller with and without batt (with the amount sold to dso, if happened)
                    #noMatch_sup[day, hour, agent_s] = noMat_s 
                    #the noMtach supply is sold to the grid (dso)  
                      
                    if seller_battery[agent_s] == 1:
                        #battery_on = seller_battery[agent_s] # 1 if the seller has batteries and wants to keep the energy to sell it in a later auction
                    #battery_on = 0 if the seller wants to sell his unmatched energy to the DSO for a min price in this auction
                       
                        #batt_curr_cap =  battery_cap[agent_s] + (noMatch_sup[day, hour, agent_s] * batt_ch_eff * batt_disch_eff) # use round trip charging and discharging eff here - current capacity of the batery
                        batt_curr_cap =  battery_cap[day, hour, agent_s] + (noMatch_sup[day, hour, agent_s] * batt_ch_eff * batt_disch_eff) #if battery_cap is a 3D array  
                    #check if the batery of the seller has available capacity. The extra is sold to the DSO with min price
                        if batt_curr_cap > battery_cap_max[agent_s]: #battery_cap_max includes the SOC_80 max charge factor
                            #battery_cap[agent_s] = battery_cap_max[agent_s]
                            battery_cap[day, hour, agent_s] = battery_cap_max[agent_s] #if battery_cap is a 3D array 
                            #noMat_s = (battery_cap[agent_s] + noMatch_sup[day, hour, agent_s]) - battery_cap_max[agent_s]
                            noMat_s = (battery_cap[day, hour, agent_s] + noMatch_sup[day, hour, agent_s]) - battery_cap_max[agent_s] #if battery_cap is a 3D array 
                            noMatch_sup[day, hour, agent_s] = noMat_s  
                        else:    
                            #battery_cap[agent_s] = batt_curr_cap
                            battery_cap[day, hour, agent_s] = batt_curr_cap #if battery_cap is a 3D array 
                            noMatch_sup[day, hour, agent_s] = 0
                            #noMatch_sup[day, hour, agent_s] = noMat_s  
                         
                         
                else: # R > 1 or so Demand > Supply
                
                    Pdeg = 0.04 # 0.04 eur/kWh - degradation cost per kWh of using the batt
                    #Ebatt_dis = battery_cap[agent_s]  
                    # so that Ebatt_dis cannot be lower that the SOC-20 of the battery of this prosumer
                    Ebatt_dis = battery_cap[day, hour, agent_s] - battery_cap_min[agent_s] #if battery_cap is a 3D array
                         
                    # profit in euro by the selling of the energy saved in battery based in current auction price
                    Pr_batt_now = (Price_kwh_eur_array[day, hour] - Pdeg) * Ebatt_dis 
                     
                    # profit in euro by the selling of the energy saved in battery based in EMA of previous 24 auction prices
                    Pr_batt_EMA = (Price_EMA[day, hour] - Pdeg) * Ebatt_dis
                           
                    #price the consumer would pay if buy that energy from the grid
                    #Pr_grid = Ebatt_dis *  conPayDSO_euro
                    
                    # Do comparisons and decide if use the batt or not
                    if Pr_batt_now > Pr_batt_EMA: #if current price is higher than EMA, then sell the battery uo to its SOC-20
                         
                        #supply_f[day, hour, agent_s] = seller_bidQuantity[day, hour, agent_s] + battery_cap[agent_s] #old code - no optimum use of batt
                        supply_f[day, hour, agent_s] = seller_bidQuantity[day, hour, agent_s] + Ebatt_dis #if battery_cap is a 3D array
  
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
                
                receive_pr_eur[day, hour, agent_s] = receive_dso_eth[day, hour, agent_s] * ETH_2_EURO #total price in euro from peers
                
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
        prosum_sup = np.sum(supply_f[day, hour, :num_seller]) #total final supply by prosumers to cons
        supply_F_array[day, hour] = prosum_sup 
        
        #consum_demand = sum(demand_f[day][hour][agent_b] for agent_b in range(num_buyer+num_seller)) #total final demand by consumers and pros to prosum
        consum_demand = np.sum(demand_f[day, hour, :num_buyer+num_seller]) #total final demand by consumers and pros to prosum
        demand_F_array[day, hour] = consum_demand
          
        initial_supply = ES #total initial supply
        initial_demand = ED #total initial demand
        
        #final_sup = sum(total_supply[day][hour][agent_s] for agent_s in range(num_seller)) #total final supply for this auction round by prosumers to cons and dso
        final_sup = np.sum(total_supply[day, hour, :num_seller]) #total final supply for this auction round by prosumers to cons and dso
        final_sup_ar[day, hour] = final_sup  
         
        #final_dem = sum(total_demand[day][hour][agent_b] for agent_b in range(num_buyer+num_seller)) #total final demand for this auction round by consumers and pros to prosum and dso
        final_dem = np.sum(total_demand[day, hour, :num_buyer+num_seller]) #total final demand for this auction round by consumers and pros to prosum and dso
        final_dem_ar[day, hour] = final_dem   
         
        #if total_supply == total_demand: print("Matching between peers ONLY is correct, Supply = Demand") 
        #else: print("Matching between peers ONLY is NOT correct, Supply different than Demand")
        """
        print("Total initial supply: {0} kWh".format(initial_supply))
        print("Total initial demand: {0} kWh \n".format(initial_demand))
        print("Total final supply (to consum + pros only): {0} kWh".format(prosum_sup))
        print("Total final demand (covered by prosum only): {0} kWh\n".format(consum_demand))
        print("Total final supply (to consum, pros + dso): {0} kWh".format(final_sup))
        print("Total final demand (covered by prosum + dso): {0} kWh\n".format(final_dem))
        """

         
        #print("Auction round of hour X of day Y is over")
        print("Auctions for DAY {0} and HOUR {1} are over. \n".format(day+1, hour+1))
 
 
"""
#############################################
## Here I declare and print the plots I want


#array that keeps only the prices for every hour of a specific seller for a specific day
rec_cons = [hour_data1[agent_s] for hour_data1 in receive_pr_eur[day]] #total price in euro from peers
rec_DSO = [hour_data2[agent_s] for hour_data2 in  receive_dso_eur[day]] #total price in euro from dso
rec_both = [hour_data3[agent_s] for hour_data3 in tot_receive_eur[day]] #total price received in euro: money prosumers get from peers and dso

#array that keeps only the bids for every hour of a specific seller for a specific day
sel_bid = [hour_data[agent_s] for hour_data in seller_bidQuantity[day]]

#array that keeps only the prices for every hour of a specific buyer for a specific day
pay_pros = [hour_data1[agent_b] for hour_data1 in pay_pr_eur[day]] #total price in euro - money cons pay to prosum
pay_DSO = [hour_data2[agent_b] for hour_data2 in  pay_dso_eur[day]] #total price in euro - money cons pay to dso
pay_both = [hour_data3[agent_b] for hour_data3 in total_pay_eur[day]] #total price in eur - money cons pay to prosum and dso

#array that keeps only the bids for every hour of a specific seller for a specific day
b_bid = [hour_data[agent_b] for hour_data in buyer_bidQuantity[day]]



for day in range(num_days):
    
    for agent_s in range(num_seller):

        ######Plot the price in euro DSO will pay to prosumers, for the energy they sold to cons, DSO and both together
        pros_rec(day, agent_s, rec_cons, rec_DSO, rec_both, num_hours)
        
        ######Plot each sellers initial bids
        seller_bid(day, agent_s, sel_bid, num_hours)
    
    
    
    for agent_b in range(num_buyer+num_seller):
        
        ######Plot the price in euro consumers pay to prosumers, DSO and both together
        consum_pay(day, agent_b, pay_pros, pay_DSO, pay_both, num_hours)
  
        ######Plot each buyers initial bids 
        buyer_bid(day, agent_b, b_bid, num_hours) 
    
       
          
 
    ##################          
    priceKWH = Price_kwh_eur_array[day] # Extract the prices for a specific day (e.g., day 3)
    R_values = R_array[day]
    sup_f_cons = supply_F_array[day] #total final supply by all prosumers to cons only in each round
    sup_f_cons_dso = final_sup_ar[day] #total final supply by all prosumers to cons and dso in each round
    cons_f_pros = demand_F_array[day] #total final demand by consumers to prosum
    cons_f_pros_dso = final_dem_ar[day]  #total final demand for this auction round by consumers to prosum and dso
    

    ## plot: common Price per kWh Values for every hour (auction round)
    price_common(day, priceKWH, num_hours)

    ## plot: R ratio Values for every hour
    R_ratio(day, R_values, num_hours)
    
    ## plot: common Price per kWh Values over R ration in every hour of the Day
    price_R(day, R_values, priceKWH)
    
    
    ##Plot the price in euro DSO will pay to prosumers, for the energy they sold to cons, DSO and both together
    supply_final(day, sup_f_cons, sup_f_cons_dso, num_hours)
      
    ## plot: final total demand by all consumers from prosumers and from pros+DSO in each hour - round
    demand_final(day, cons_f_pros, cons_f_pros_dso, num_hours)
    """
    
    

#calculate the average price per kWh for the whole period of the auctions
avePrice = avePrice = np.mean(Price_kwh_eur_array) #average price of the whole period (days and hours) in euro 
print("Average price: {:.2f}".format(avePrice))

     
# End the timer
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time    

# Print the elapsed time
print("Elapsed time: {:.2f} seconds".format(elapsed_time))   
 







