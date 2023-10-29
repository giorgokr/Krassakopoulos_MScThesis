# this one needs to be called by the file "SC_bids_pay_auto_v5"

#import math
import numpy as np 

def price(p_balance, p_con, R, k, ETH_2_EURO, ether, minPrice_DSO):
    p_calc = ((2/np.pi) * p_con * np.arctan((np.log(R))**k)) + p_balance
    
    if p_calc > minPrice_DSO:
        p = p_calc
        
    else:
        #p_min = 0.01 #set the min price per in LEM to be 0.01 euro or 1 cent
        #p = (p_min / ETH_2_EURO) * ether
        p = minPrice_DSO 
        
        
    return p




 
























"""
def price(buyerarray,sellerarray):
    a = int(np.mean([buyerarray[0], sellerarray[0]]) * np.min([buyerarray[1] * sellerarray[1]]))
    return a
"""
