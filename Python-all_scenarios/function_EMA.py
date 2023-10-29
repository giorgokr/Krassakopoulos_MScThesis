#from function_avePrice_year import avePrice_0 

def find_EMA(day, hour, num_days, num_hours, num_buyer, num_seller, Price_EMA, 
            Price_kwh_eur_array, batt_ch_eff, batt_disch_eff): 
     
    # calculate and keep record of the EMA prices, to use in the auctions
    time_periods = 24 # number of hours the EMA includes
    mult = 2 / (time_periods + 1) # the weighting multiplier we use in the EMA
    #price used for EMA calc when hour=0 and day = 0
    #Price_ave0 = avePrice_0(num_days, num_hours, num_seller, num_buyer, batt_ch_eff, batt_disch_eff) 
    Price_ave0 = 0.16
    if day == 0 and hour == 0:   
        Price_EMA[day, hour] = (Price_kwh_eur_array[day, hour] * mult) + (Price_ave0 * (1-mult))
    else: #for the very first time, when hour = 0 and I do not have previous data
        Price_EMA[day, hour] = (Price_kwh_eur_array[day, hour] * mult) + (Price_EMA[day, hour-1] * (1-mult))
       
        #in different file feed it with the prices for one year based only in supply and demand
        #from these calculate only SMA or EMA and use it as the yesterday EMA for the hour = 0 case
         
    return Price_EMA , Price_ave0    
 