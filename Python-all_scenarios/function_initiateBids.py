#import numpy as np

def initiate_Bids(bb, day, hour, num_seller, num_buyer, pros_gen, battery_cap, battery_cap_min, pros_dem_ini, cons_dem, pros_dem_f,
                  buyer_bidQuantity, seller_bidQuantity):
      
    for agent_s in range(num_seller):
        a = pros_gen[day, hour, agent_s] 
        
        if hour == 0 and day == 0:
            b = battery_cap[day, hour, agent_s] - battery_cap_min[agent_s] #should include also the 20% min SOC
            bb[day, hour, agent_s] = b
        elif hour > 0:
            b = battery_cap[day, hour-1, agent_s] - battery_cap_min[agent_s] #should include also the 20% min SOC
            bb[day, hour, agent_s] = b
        elif hour == 0 and day > 0:
            b = battery_cap[day-1, 23, agent_s] - battery_cap_min[agent_s] #should include also the 20% min SOC
            bb[day, hour, agent_s] = b
             
        k = pros_dem_ini[day, hour, agent_s]
        
        pd = k - a - b   
        pros_dem_f[day, hour, agent_s] = max(pd, 0) 
        buyer_bidQuantity[day, hour, agent_s] = pros_dem_f[day, hour, agent_s] 
        #sbQ = a + b - k # including batteries in the sellers energy offer
        sbQ = a - k # not including batteries in the sellers energy offer
        seller_bidQuantity[day, hour, agent_s] = max(sbQ, 0)
             
    i = 0
    for agent_b in range(num_seller, num_seller + num_buyer):
        buyer_bidQuantity[day, hour, agent_b] = cons_dem[day, hour, i]
        i += 1
    
    return buyer_bidQuantity, seller_bidQuantity, pros_dem_f, bb  

