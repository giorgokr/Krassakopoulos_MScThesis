import pandas as pd
import numpy as np
#import random


def energy_offer(num_days, num_hours, num_seller, panels_num):
    
    # Load the data Series from the Excel file
    ghi_Archal = pd.read_excel('solcast_ghi_Archalochori.xlsx')
    ambTemp_Archal = pd.read_excel('solcast_Air Temp_Archalochori.xlsx')
    
    # Convert the DataFrame column to a NumPy array - make it mix from different locations
    ghi_nparray = ghi_Archal['Ghi'].values
    ambTemp_nparray = ambTemp_Archal['AirTemp'].values
    
    A_mod = 1.754 * 1.096 # area (m2) of one module of the ones I use
    n_inv = 0.98 #efficiency of inverter
    T_noct = 43 # NOCT temp in deg celcius
    Ta_noct = 20 # ambient NOCT temp in deg celcius
    G_noct = 800 # irradiance in W/m2 under NOCT consitions
    n_e = 0.208 # efficiency of the module 
    ta = 0.9 # τα product, we use standard the value 0.9
    P_stc = 400 # power gen by one module in W, under STC conditions
    G_stc = 1000 # irradiance in W/m2 under STC consitions
    c_temp = - 0.0034 # temp coefficient of Pmax = -0.34% per deg Celcius
    Tc_stc = 25 # cell temp under STC consitions
    # Tc is the PV module (or cell) temperature
    # G is the irradiance GHI in W/m2 at time t one the panel
    G = ghi_nparray
    #G = 630
    #G = np.array([630, 1000, 1100])
    
    # Ta is the ambient temprature
    Ta = ambTemp_nparray
       
    #Power generation calculation by each module - by one module in W
    #For the formulas I used Kalogirou, notes L03 from solar course, sources f5 and f6, check also notes on day book
    Tc = (T_noct - Ta_noct) * (G/G_noct) * (1 - (n_e/ta)) + Ta
    P_mod_m2 = P_stc * (G/G_stc) * (1 + c_temp * (Tc - Tc_stc)) #power generated per m2 of a module
    P_mod = P_mod_m2 * A_mod #power generated by one module
    P_gen = n_inv * P_mod # power generated after the inverter and its losses
    E_gen = np.round(P_gen * 1 / 1000, 6) # energy generated by the P_gen in every hour - energy by one module - kWh = W*h/1000
    #with the np.round it shows up to 6 decimal places max
    
    
    #compute energy generated by each seller ...
    
    
    # vector with sellers' energy generation in each hour
    #energy_gen = [[[0 for _ in range(num_seller)] for _ in range(num_hours)] for _ in range(num_days)]
    energy_gen = np.zeros((num_days, num_hours, num_seller)) 
    
    
    # Iterate over each day, hour, and agent, and update seller_bidQuantity with E_gen values and panels_num
    #it computes the total energy bidded by each seller
    index = 0
    for day in range(num_days):
        for hour in range(num_hours):
            for agent_s in range(num_seller):
                energy_gen[day, hour, agent_s] = (E_gen[index] * panels_num[agent_s])
                # multiply with number of panels / I compute the round to the nearest int
                #in order to have int so that solidity can work with it
                #seller_bidQuantity[day][hour][agent_s] = E_gen[index % len(E_gen)] * panels_num[agent_s]  
            index += 1
                
    return energy_gen, E_gen
   

           

