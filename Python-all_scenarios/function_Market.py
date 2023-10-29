import time 
from Price_to_Pay_v5 import price
from avePrice_year import avePrice_0 
#import random
#import matplotlib.pyplot as plt
import numpy as np
 
#continue

def call_Market(day, hour, num_days, num_hours, num_seller, num_buyer, buyer_bidQuantity, seller_bidQuantity, ED_array, ES_array, 
                battery_cap, R_array, Price_kwh_array, Price_kwh_eth_array,  Price_kwh_eur_array, Price_EMA, supply_f,  noMatch_sup, 
                seller_battery, 
                total_supply, batt_ch_eff, batt_disch_eff, battery_cap_max, battery_cap_min, receive_pr, receive_dso, receive_pr_eth, 
                receive_dso_eur, receive_dso_eth, receive_pr_eur, tot_receive, tot_receive_eth, tot_receive_eur, demand_f,
                demand_dso, total_demand,  pay_pr, pay_dso, pay_pr_eth, pay_dso_eth, pay_pr_eur, pay_dso_eur, total_pay, total_pay_eth, 
                total_pay_eur, supply_F_array, demand_F_array, final_sup_ar, final_dem_ar): 
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