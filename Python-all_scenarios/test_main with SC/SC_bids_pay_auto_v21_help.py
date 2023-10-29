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
#This code .v21_help is the same with v20_help but I do for up to 99 pros and cons
  
import time 
import json
#import time
#import pprint
from web3 import Web3
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
 
def deploy_contract(w3, contract_interface):
    tx_hash = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
        ).constructor().transact()
        #functions.transact() executes the specified function by sending a new public transaction.
    address = w3.eth.wait_for_transaction_receipt(tx_hash)['contractAddress']
    return address

#ether = 10**18 # 1 ether = 1000000000000000000 wei

# Connection to he Local Ganache Blockchain
ganache_url = "HTTP://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(ganache_url))
print(w3.is_connected())
print(w3.eth.block_number)

 
## We define the agent's accounts
# The operator/DSO:
w3.eth._default_account = w3.eth.accounts[0]
DsoAgentAccount = w3.eth._default_account
  
# Number of days in a year
num_days = 1
# Number of hours in a day
num_hours = 1
num_seller = 49 # declare the number of sellers
num_buyer = 50 # declare the number of buyers
   
#seller = [0] * num_seller
#seller = np.full(num_seller, 0)
seller = np.zeros((num_seller), dtype = object)
#buyer = [0] * num_buyer
#buyer = np.full(num_buyer, 0) 
buyer = np.zeros((num_buyer), dtype = object)

# The Seller:
#for i in range(0, 4, 1):
for i in range(num_seller):
    #print(i+1)
    seller[i] = w3.eth.accounts[i+1]
    
# The Buyer:
#for j in range(0, 4, 1):
for j in range(num_buyer):
    #print(j+5)
    buyer[j] = w3.eth.accounts[j+num_seller+1]


# to Compile the contract - from SC .v6
contract_interface = { # I create this dictionary and I put in hand, the values the the above would take automatically from the SC
    'abi': json.loads('[{"inputs":[],"stateMutability":"payable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"accountAddress","type":"address"},{"indexed":false,"internalType":"uint256","name":"quantity","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"Weight","type":"uint256"}],"name":"LogBidMade","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":true,"internalType":"address","name":"receiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"energyAmount","type":"uint256"}],"name":"LogEnergyTransferred","type":"event"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"agentType","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address payable","name":"agentaddress","type":"address"}],"name":"close","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"closecontract","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"currState","outputs":[{"internalType":"enum NegotiationMarketPlace.State","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"dsoAgent","outputs":[{"internalType":"address payable","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"index","type":"uint256"}],"name":"getTransaction","outputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"agentaddress","type":"address"}],"name":"getbalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"agentaddress","type":"address"}],"name":"getrealbalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"marketEndTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"operationaldeposit","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"agentaddress","type":"address"}],"name":"retrievebid","outputs":[{"internalType":"uint256[4]","name":"","type":"uint256[4]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"senderAddress","type":"address"},{"internalType":"address payable","name":"receivAddress","type":"address"},{"internalType":"uint256","name":"pay_price","type":"uint256"},{"internalType":"uint256","name":"energyAmount","type":"uint256"}],"name":"settlement","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_bidquantity","type":"uint256"},{"internalType":"uint256","name":"_bidweight","type":"uint256"},{"internalType":"uint256","name":"_agenttype","type":"uint256"}],"name":"submitBid","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"transactions","outputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"uint256","name":"energyAmount","type":"uint256"},{"internalType":"bool","name":"verified","type":"bool"}],"stateMutability":"view","type":"function"}]'),
    'bin': '6080604052600780546101003302610100600160a81b03199091161790556000805461ffff19169055610a71806100376000396000f3fe6080604052600436106100dd5760003560e01c806359d202141161007f5780639ace38c2116100595780639ace38c2146102ef578063ad7f33af14610319578063afe010431461034a578063c74073a114610383576100dd565b806359d202141461027457806368116177146102a757806369c41a74146102da576100dd565b806333ea3dc8116100bb57806333ea3dc81461017a5780633ce8565f146101d8578063416f222a146101e057806343ba7b2914610209576100dd565b80630fbd7aed146100e257806315f427c3146100ec57806329e6fefc14610135575b600080fd5b6100ea6103a9565b005b3480156100f857600080fd5b506100ea6004803603608081101561010f57600080fd5b506001600160a01b03813581169160208101359091169060408101359060600135610432565b34801561014157600080fd5b506101686004803603602081101561015857600080fd5b50356001600160a01b03166105d6565b60408051918252519081900360200190f35b34801561018657600080fd5b506101a46004803603602081101561019d57600080fd5b50356105e8565b604080516001600160a01b039586168152939094166020840152828401919091521515606082015290519081900360800190f35b610168610699565b610168600480360360608110156101f657600080fd5b50803590602081013590604001356106fa565b34801561021557600080fd5b5061023c6004803603602081101561022c57600080fd5b50356001600160a01b031661077e565b6040518082608080838360005b83811015610261578181015183820152602001610249565b5050505090500191505060405180910390f35b34801561028057600080fd5b506101686004803603602081101561029757600080fd5b50356001600160a01b031661083a565b3480156102b357600080fd5b50610168600480360360208110156102ca57600080fd5b50356001600160a01b0316610884565b3480156102e657600080fd5b5061016861089f565b3480156102fb57600080fd5b506101a46004803603602081101561031257600080fd5b50356108a5565b34801561032557600080fd5b5061032e6108eb565b604080516001600160a01b039092168252519081900360200190f35b34801561035657600080fd5b5061035f6108ff565b6040518082600481111561036f57fe5b60ff16815260200191505060405180910390f35b6100ea6004803603602081101561039957600080fd5b50356001600160a01b0316610908565b60075461010090046001600160a01b031633146103fb576040805162461bcd60e51b81526020600482018190526024820152600080516020610a1c833981519152604482015290519081900360640190fd5b6001805460405133916000190180156108fc02916000818181858888f1935050505015801561042e573d6000803e3d6000fd5b5050565b60075461010090046001600160a01b03163314610484576040805162461bcd60e51b81526020600482018190526024820152600080516020610a1c833981519152604482015290519081900360640190fd5b6001600160a01b0384166000908152600560205260409020548210156105d0576001600160a01b0380841660008181526005602090815260408083208054880190558885168084528184208054899003905581516080810183529485529184019182528301858152600160608501818152600680549283018155909452935160049094027ff652222313e28459528d920b65115c16c04f3efc82aaedc97be59f3f377c0d3f810180549587166001600160a01b031996871617905591517ff652222313e28459528d920b65115c16c04f3efc82aaedc97be59f3f377c0d40830180549190961694169390931790935590517ff652222313e28459528d920b65115c16c04f3efc82aaedc97be59f3f377c0d41830155517ff652222313e28459528d920b65115c16c04f3efc82aaedc97be59f3f377c0d42909101805491151560ff199092169190911790555b50505050565b60046020526000908152604090205481565b6000806000806006805490508510610647576040805162461bcd60e51b815260206004820152601960248201527f496e76616c6964207472616e73616374696f6e20696e64657800000000000000604482015290519081900360640190fd5b60006006868154811061065657fe5b600091825260209091206004909102018054600182015460028301546003909301546001600160a01b0392831698509116955090935060ff169150509193509193565b60075460009061010090046001600160a01b031633146106ee576040805162461bcd60e51b81526020600482018190526024820152600080516020610a1c833981519152604482015290519081900360640190fd5b50600180543401815590565b60008160011415610720576000805460ff8082166001011660ff19909116179055610740565b6000805460ff61010080830482166001019091160261ff00199091161790555b503360009081526002602090815260408083209590955560038152848220939093556004808452848220928355600584529390203490559190525490565b6107866109fd565b60075461010090046001600160a01b031633146107d8576040805162461bcd60e51b81526020600482018190526024820152600080516020610a1c833981519152604482015290519081900360640190fd5b6107e06109fd565b5050604080516080810182526001600160a01b039290921660008181526002602090815283822054855282825260038152838220548186015282825260048152838220548585015291815260059091522054606082015290565b60075460009081906001600160a01b03848116610100909204161461086a57506001600160a01b0382163161087e565b5060075461010090046001600160a01b0316315b92915050565b6001600160a01b031660009081526005602052604090205490565b60085481565b600681815481106108b257fe5b600091825260209091206004909102018054600182015460028301546003909301546001600160a01b0392831694509116919060ff1684565b60075461010090046001600160a01b031681565b60075460ff1681565b60075461010090046001600160a01b0316331461095a576040805162461bcd60e51b81526020600482018190526024820152600080516020610a1c833981519152604482015290519081900360640190fd5b6007546001600160a01b0382811661010090920416146109ba576001600160a01b03811660008181526005602052604080822054905181156108fc0292818181858888f193505050501580156109b4573d6000803e3d6000fd5b506109fa565b6007546001546040516101009092046001600160a01b0316916108fc82150291906000818181858888f1935050505015801561042e573d6000803e3d6000fd5b50565b6040518060800160405280600490602082028036833750919291505056fe4f6e6c792044534f2f4f70657261746f722063616e2063616c6c20746869732ea264697066735822122081b5f13529284b6f1c84cbcaf159e51a82b5bad1952076f9ae494908678f651264736f6c63430006060033'
}

# retrieve the compilation results (abi and bytecode)
abi = contract_interface['abi']
bytecode = contract_interface['bin']
 
 
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
pros_gen = np.random.uniform(1, 3, size=(num_days, num_hours, num_seller))


  

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
   
 
## Needed arrays for when the Operator/DSO retrieves the bids 
seller_Data = np.zeros((num_days, num_hours, num_seller), dtype = object)
seller_bal = np.zeros((num_days, num_hours, num_seller))
seller_bal_eth = np.zeros((num_days, num_hours, num_seller))
seller_en_bal = np.zeros((num_days, num_hours, num_seller))
seller_en_bal_eth = np.zeros((num_days, num_hours, num_seller))
seller_real_bal = np.zeros((num_days, num_hours, num_seller))
seller_real_bal_eth = np.zeros((num_days, num_hours, num_seller))
  
buyer_Data = np.zeros((num_days, num_hours, num_buyer), dtype = object) 
buyer_bal = np.zeros((num_days, num_hours, num_buyer))
buyer_bal_eth = np.zeros((num_days, num_hours, num_buyer))
buyer_en_bal = np.zeros((num_days, num_hours, num_buyer))
buyer_en_bal_eth = np.zeros((num_days, num_hours, num_buyer))
buyer_real_bal = np.zeros((num_days, num_hours, num_buyer))
buyer_real_bal_eth = np.zeros((num_days, num_hours, num_buyer))


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
        
        # Deployment of the contract
        address = deploy_contract(w3, contract_interface)
        contract = w3.eth.contract(
            address = address,
            abi = abi
        )

        #the deposit by the DSO is being made
        tx = { 
        # dictionary with the info of the transaction that we will make -- for details what each of them means look web3 from yt _tut3 
        #python code file
              'from': DsoAgentAccount,
              'to': address,
              'value': w3.to_wei(1,'ether'),
              'gas': 2000000,
              'gasPrice': w3.to_wei('20','gwei'),
        }
        tx_hash = contract.functions.operationaldeposit().transact(tx)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
         
        
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
            #seller_bidQuantity[day][hour][agent_s] = [x + y - v for x, y, v in zip(a, b, k)]
            #quantity = seller_bidQuantity[day][hour][agent_s] # it makes 0 even the ones who need to buy energy
            quantity = int(sbQ * 10**6) # it has as zero only the ones who neither sell or buy - # to avoid input float in solidity I do kWh * 10**6 to have an int
              
            # prosumers who will sell energy make their offer (bid) 
            if quantity >= 0: # look at notes textbook why I put >=
                weight = int(seller_bidWeight[day, hour, agent_s]) 
                agnt_type = int(agent_type[0])  
                gas_estimate[day, hour, agent_s] = contract.functions.submitBid(quantity, weight, agnt_type).estimate_gas()
                  
                #in .submitBid() the arguments are:
                # arg(1) =10 is the bid price - price per kWh (integer) -> removed from this script
                # arg(2) =10 is the bidQuantity - energy quantity in kWh (integer)
                # arg(3) =1 is the bidWeight
                # arg(4) =0 is the agent type (0 for seller, 1 for buyer)
                
                #print("Gas estimate, for offer by Seller {0}, Day {1}, Hour {2} to transact with submitBid: {3}\n".format(agent_s+1, day+1, hour+1, gas_est))
         
                if gas_estimate[day, hour, agent_s] < 200000:
            
                    # The seller submits his offer:
                    #print("Submitting Offer from Seller {0}, Day {1}, Hour {2}".format(agent_s+1, day+1, hour+1))
                    tx_hash = contract.functions.submitBid(quantity, weight, agnt_type).transact({'from': seller[agent_s]}) 
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                else:
                  print("Gas cost exceeds 200000")
                  #maybe I should end the program here if this "else" occur or not?
                
                # First retrieves the sellers' bids for that hour of the day
                tx_hash = contract.functions.retrievebid(seller[agent_s]).transact()
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                seller_Data[day, hour, agent_s] = contract.functions.retrievebid(seller[agent_s]).call() #become 3d
                # We display the sellers' account balance:
                seller_bal[day, hour, agent_s] = contract.functions.getbalance(seller[agent_s]).call() #become 3d
                seller_bal_eth[day, hour, agent_s] = w3.from_wei(seller_bal[day, hour, agent_s], "ether") #become 3d
                #print("Seller's {0} deposit account Balance (eth): {1}\n".format(agent_s+1, seller_bal_eth[day][hour][agent_s]))
            
            #Each prosumer-buyer makes a deposit 
                 
            #quantity = buyer_bidQuantity[day][hour][agent_s] # it makes 0 even the ones who sell energy
            quantity = int(pd * 10**6) # to avoid input float in solidity I do kWh * 10**6 to have an int
            
            if quantity > 0: 
                weight = int(seller_bidWeight[day, hour, agent_s]) 
                agnt_type = int(agent_type[0])  
                 
                #here I need to include also the pros who will buy in this round
                tx = {
                      'from': seller[agent_s], 
                      'to': address,
                      'value': w3.to_wei(0.3,'ether'), #buyer puts 1 eth in his deposit expressed as wei
                      'gas': 2000000,
                      'gasPrice': w3.to_wei('20','gwei'),
                } 
                # The proseumer-buyer submits his bid:
                #print("Submitting Bid from Buyer {0}, Day {1}, Hour {2}\n".format(agent_b+1, day+1, hour+1))       
                tx_hash = contract.functions.submitBid(quantity, weight, agnt_type).transact(tx)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                         
                # Then retrieves the prosumer-Buyer's bid
                tx_hash = contract.functions.retrievebid(seller[agent_s]).transact()
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                seller_Data[day, hour, agent_s] = contract.functions.retrievebid(seller[agent_s]).call() #become 3d 
                # we check that the DSO retrieve the buyer's 
                #print("Buyer's {0} bid: {1}\n".format(agent_b+1, buyer_Data[day][hour][agent_b]))
                # We display the buyers' account balance: 
                seller_bal[day, hour, agent_s] = contract.functions.getbalance(seller[agent_s]).call() #become 3d
                seller_bal_eth[day, hour, agent_s] = w3.from_wei(seller_bal[day, hour, agent_s], "ether") #become 3d
                #print("Pros-Buyer's {0} deposit account Balance (eth): {1}\n".format(agent_s+1, seller_bal_eth[day][hour][agent_s])) 
                  
        # fill the buyer_bidQuantity array-list    
        i = 0
        for agent_b in range(num_seller, num_seller + num_buyer): 
            #agent_b values starting from "num_seller" up to "num_seller + num_buyer - 1"
               
            buyer_bidQuantity[day, hour, agent_b] = cons_dem[day, hour, i] 
             
              
        #Each consumer-buyer makes a deposit 
              
            #get_quantity = buyer_bidQuantity[day, hour, agent_b]
            quantity = int(buyer_bidQuantity[day, hour, agent_b] * 10**6) # to avoid input float in solidity I do kWh * 10**6 to have an int
            weight = int(buyer_bidWeight[day, hour, i])
            agnt_type = int(agent_type[1]) 
              
            #here I need to include also the pros who will buy in this round
            tx = {
                  'from': buyer[i], 
                  'to': address,
                  'value': w3.to_wei(0.3,'ether'), #buyer puts 1 eth in his deposit expressed as wei
                  'gas': 2000000,
                  'gasPrice': w3.to_wei('20','gwei'),
            } 
            # The buyer submits his bid:
            #print("Submitting Bid from Buyer {0}, Day {1}, Hour {2}\n".format(agent_b+1, day+1, hour+1))       
            tx_hash = contract.functions.submitBid(quantity, weight, agnt_type).transact(tx)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
              
            # Then retrieves the Buyer's bid
            tx_hash = contract.functions.retrievebid(buyer[i]).transact()
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            buyer_Data[day, hour, i] = contract.functions.retrievebid(buyer[i]).call() #become 3d
            # we check that the DSO retrieve the buyer's 
            #print("Buyer's {0} bid: {1}\n".format(agent_b+1, buyer_Data[day][hour][agent_b]))
            # We display the buyers' account balance: 
            buyer_bal[day, hour, i] = contract.functions.getbalance(buyer[i]).call() #become 3d
            buyer_bal_eth[day, hour, i] = w3.from_wei(buyer_bal[day, hour, i], "ether") #become 3d
            #print("Buyer's {0} deposit account Balance (eth): {1}\n".format(i+1, buyer_bal_eth[day][hour][i]))
     
             
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
                    #supply_f[day, hour, agent_s] = R * seller_bidQuantity[day, hour, agent_s]
                    noMatch_sup[day, hour, agent_s] = seller_bidQuantity[day, hour, agent_s] - supply_f[day, hour, agent_s] # the unmatched supply of the seller with and without batt (with the amount sold to dso, if happened)
                    #noMatch_sup[day, hour, agent_s] = noMat_s 
                    #the noMtach supply is sold to the grid (dso)  
                      
                    if seller_battery[agent_s] == 1:
                        #battery_on = seller_battery[agent_s] # 1 if the seller has batteries and wants to keep the energy to sell it in a later auction
                    #battery_on = 0 if the seller wants to sell his unmatched energy to the DSO for a min price in this auction
                       
                        #batt_curr_cap =  battery_cap[agent_s] + (noMatch_sup[day, hour, agent_s] * batt_ch_eff * batt_disch_eff) # use round trip charging and discharging eff here - current capacity of the batery
                        batt_curr_cap =  battery_cap[day, hour, agent_s] + (noMatch_sup[day, hour, agent_s] * batt_ch_eff * batt_disch_eff) #if battery_cap is a 3D array  
                    #check if the batery of the seller has available capacity. The extra is sold to the DSO with min price
                        if batt_curr_cap > battery_cap_max[agent_s]:
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
                     
                    if Pr_batt_now > Pr_batt_EMA:
                         
                        supply_f[day, hour, agent_s] = seller_bidQuantity[day, hour, agent_s] + Ebatt_dis #old code - no optimum use of batt
                        #supply_f[day, hour, agent_s] = sup_f
                        noMatch_sup[day, hour, agent_s] = 0
                        #noMatch_sup[day, hour, agent_s] = noMat_s 
                         
                    else:
                        supply_f[day, hour, agent_s] = seller_bidQuantity[day, hour, agent_s]
                        #supply_f[day, hour, agent_s] = sup_f
                        noMatch_sup[day, hour, agent_s] = 0
                        #noMatch_sup[day, hour, agent_s] = noMat_s
                         
                    
                total_supply[day, hour, agent_s] = supply_f[day, hour, agent_s] + noMatch_sup[day, hour, agent_s] # total energy sold (induced to the grid - peers and dso) by the prosumers
                #total_supply[day, hour, agent_s] = tot_sup 
                
                # compute the final price each seller will receive
                receive_pr[day, hour, agent_s] = supply_f[day, hour, agent_s] * Price_kwh #total price in wei: money prosumers get from peers  
                #receive_pr[day, hour, agent_s] = rec_pr
                  
                receive_dso[day, hour, agent_s] = noMatch_sup[day, hour, agent_s] * minPrice_DSO  #total price in wei: money prosumers get from DSO 
                #receive_dso[day, hour, agent_s] = rec_dso
                
                receive_pr_eth[day, hour, agent_s] = receive_pr[day, hour, agent_s] / 10**18 #total price in eth from peers
                #receive_pr_eth[day, hour, agent_s] = rec_pr_eth
                 
                receive_dso_eth[day, hour, agent_s] = receive_dso[day, hour, agent_s] / 10**18 #total price in eth from dso
                #receive_dso_eth[day, hour, agent_s] = rec_dso_eth
                 
                receive_pr_eur[day, hour, agent_s] = receive_dso_eth[day, hour, agent_s] * ETH_2_EURO #total price in euro from peers
                #receive_pr_eur[day, hour, agent_s] = rec_pr_eur
                  
                receive_dso_eur[day, hour, agent_s] = receive_dso_eth[day, hour, agent_s] * ETH_2_EURO #total price in euro from dso
                #receive_dso_eur[day, hour, agent_s] = rec_dso_eur
                          
                tot_receive[day, hour, agent_s] = receive_pr[day, hour, agent_s] +  receive_dso[day, hour, agent_s]  #total price received in wei: money prosumers get from peers and dso 
                #tot_receive[day, hour, agent_s] = tot_rec #int(tot_rec)
                tot_receive_eth[day, hour, agent_s] = receive_pr_eth[day, hour, agent_s] + receive_dso_eth[day, hour, agent_s] #total price received in eth: money prosumers get from peers and dso
                #tot_receive_eth[day, hour, agent_s] = tot_rec_eth
                tot_receive_eur[day, hour, agent_s] = receive_pr_eur[day, hour, agent_s] + receive_dso_eur[day, hour, agent_s] #total price received in euro: money prosumers get from peers and dso
                #tot_receive_eur[day, hour, agent_s] = tot_rec_eur   
                
                #print("Seller {0} has no matched supply of {1} kWh".format(agent_s+1, noMat_s))
                #print("Prosumer {0} will total sell {1} kWh and total receive {2} ETH or {3} EURO\n".format(agent_s+1, tot_sup, tot_rec_eth, tot_rec_eur))
                 
                 
            #for prosumers who buy
            if seller_bidQuantity[day, hour, agent_s] == 0:
                if R <= 1: # so Demand <= Supply 
                    demand_f[day, hour, agent_s] = buyer_bidQuantity[day, hour, agent_s]  
                    #demand_f[day, hour, agent_s] = dem_f
                    demand_dso[day, hour, agent_s] = 0 #demand that will be covered by dso
                    #demand_dso[day, hour, agent_s] = dem_dso
                
 
                else: # R > 1 or Demand > Supply
                    demand_f[day, hour, agent_s] = buyer_bidQuantity[day, hour, agent_s] / R #demand of prosumer that will be covered by other prosumers
                    #demand_f[day, hour, agent_s] = dem_f
                    demand_dso[day, hour, agent_s] = buyer_bidQuantity[day, hour, agent_s] - demand_f[day, hour, agent_s] #demand that will be covered by dso
                    #demand_dso[day, hour, agent_s] = dem_dso
               
                 
                total_demand[day, hour, agent_s] = demand_f[day, hour, agent_s] + demand_dso[day, hour, agent_s] #total demand by prossumer x of this round that will be covered by prosum and dso
                #total_demand[day, hour, agent_s] = tot_dem
  
     
                # compute the final price each prosumer who needs to buy in this round will pay
                pay_pr[day, hour, agent_s] = demand_f[day, hour, agent_s] * Price_kwh
                #pay_pr[day, hour, agent_s] = pay_price
                 
                pay_dso[day, hour, agent_s] = demand_dso[day, hour, agent_s] * conPay_dso #total price in wei - money pros pay to dso
                #pay_dso[day, hour, agent_s] = p_dso 
                 
                pay_pr_eth[day, hour, agent_s] = pay_pr[day, hour, agent_s] / 10**18 #total price in eth - money pros pay to prosum 
                #pay_pr_eth[day, hour, agent_s] = pay_price_eth 
                  
                pay_dso_eth[day, hour, agent_s] =  pay_dso[day, hour, agent_s] / 10**18 #total price in eth - money pros pay to dso
                #pay_dso_eth[day, hour, agent_s] = p_dso_eth
                 
                pay_pr_eur[day, hour, agent_s] = pay_pr_eth[day, hour, agent_s] * ETH_2_EURO #total price in euro - money pros pay to prosum 
                #pay_pr_eur[day, hour, agent_s] = pay_price_eur
                
                pay_dso_eur[day, hour, agent_s] = pay_dso_eth[day, hour, agent_s] * ETH_2_EURO #total price in euro - money pros pay to dso
                #pay_dso_eur[day, hour, agent_s] = p_dso_eur
                   
                total_pay[day, hour, agent_s] = pay_pr[day, hour, agent_s] + pay_dso[day, hour, agent_s] #total price in wei - money cons pay to prosum and dso
                #total_pay[day, hour, agent_s] = tot_pay #int(tot_pay)
                total_pay_eth[day, hour, agent_s] =  pay_pr_eth[day, hour, agent_s] + pay_dso_eth[day, hour, agent_s] #total price in eth - money cons pay to prosum and dso
                #total_pay_eth[day, hour, agent_s] = tot_pay_eth      
                total_pay_eur[day, hour, agent_s] = pay_pr_eur[day, hour, agent_s] + pay_dso_eur[day, hour, agent_s] #total price in eur - money cons pay to prosum and dso
                #total_pay_eur[day, hour, agent_s] = tot_pay_eur 
                 
                print("Prosumer {0} will buy {1} kWh and total pay {2} ETH or {3} EURO\n".format(agent_s+1, total_demand[day, hour, agent_s], total_pay_eth[day, hour, agent_s], total_pay_eur[day, hour, agent_s]))
  
     
        #stayed here - 04/06/2023 - at the following you need to fix the indexes in the arrays to search after
        #the prosumers who have already been placed in their cells - what about prosumers who are 0 demand and supply?
        
        #find the final amount of energy actually bought (demand) by each consumer (buyer)
        
        for agent_b in range(num_seller, num_buyer+num_seller):
            #dem_f is the demand that will be covered by the available supply of the prosumers
            if R <= 1: # so Demand <= Supply 
                demand_f[day, hour, agent_b] = buyer_bidQuantity[day, hour, agent_b]
                #demand_f[day, hour, agent_b] = dem_f
                demand_dso[day, hour, agent_b] = 0 #demand that will be covered by dso
                #demand_dso[day, hour, agent_b] = dem_dso 
            else: # in this case, R>1, so buyer_bidQuantity > Supply / # so Demand > Supply 
                demand_f[day, hour, agent_b] = buyer_bidQuantity[day, hour, agent_b] / R #demand that will be covered by prosumers
                #demand_f[day, hour, agent_b] = dem_f
                demand_dso[day, hour, agent_b] = buyer_bidQuantity[day, hour, agent_b] - demand_f[day, hour, agent_b] #demand that will be covered by dso
                #demand_dso[day, hour, agent_b] = dem_dso
                  
            total_demand[day, hour, agent_b] = demand_f[day, hour, agent_b] + demand_dso[day, hour, agent_b] #total demand by consumer x of this round that will be covered by prosum and dso
            #total_demand[day, hour, agent_b] = tot_dem
                    
            # compute the final price each buyer will pay
            pay_pr[day, hour, agent_b] = demand_f[day, hour, agent_b] * Price_kwh #total price in wei - money cons pay to prosum  
            #pay_pr[day, hour, agent_b] = pay_price 
              
            pay_dso[day, hour, agent_b] = demand_dso[day, hour, agent_b] * conPay_dso #total price in wei - money cons pay to dso
            #pay_dso[day, hour, agent_b] = p_dso   
             
            pay_pr_eth[day, hour, agent_b] = pay_pr[day, hour, agent_b] / 10**18 #total price in eth - money cons pay to prosum 
            #pay_pr_eth[day, hour, agent_b] = pay_price_eth 
            
            pay_dso_eth[day, hour, agent_b] = pay_dso[day, hour, agent_b] / 10**18 #total price in eth - money cons pay to dso
            #pay_dso_eth[day, hour, agent_b] = p_dso_eth
             
            pay_pr_eur[day, hour, agent_b] = pay_pr_eth[day, hour, agent_b] * ETH_2_EURO #total price in euro - money cons pay to prosum 
            #pay_pr_eur[day, hour, agent_b] = pay_price_eur
             
            pay_dso_eur[day, hour, agent_b] = pay_dso_eth[day, hour, agent_b] * ETH_2_EURO #total price in euro - money cons pay to dso
            #pay_dso_eur[day, hour, agent_b] = p_dso_eur
               
            total_pay[day, hour, agent_b] = pay_pr[day, hour, agent_b] + pay_dso[day, hour, agent_b] #total price in wei - money cons pay to prosum and dso
            #total_pay[day, hour, agent_b] = tot_pay #int(tot_pay)
              
            total_pay_eth[day, hour, agent_b] = pay_pr_eth[day, hour, agent_b] + pay_dso_eth[day, hour, agent_b] #total price in eth - money cons pay to prosum and dso
            #total_pay_eth[day, hour, agent_b] = tot_pay_eth       
             
            total_pay_eur[day, hour, agent_b] = pay_pr_eur[day, hour, agent_b] + pay_dso_eur[day, hour, agent_b] #total price in eur - money cons pay to prosum and dso
            #total_pay_eur[day, hour, agent_b] = tot_pay_eur 
              
            print("Consumer {0} will buy {1} kWh and total pay {2} ETH or {3} EURO\n".format(agent_b + 1 - num_seller, total_demand[day, hour, agent_b], total_pay_eth[day, hour, agent_b], total_pay_eur[day, hour, agent_b])) 

 
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
    

########### here ends the auctions and trading

# Then, we will proceed to the payment using the Smart Contract:
     
        #buyer pays the whole amount to DSO (both for the prosum and the dso)
        for agent_b in range(num_seller , num_buyer+num_seller):
            tx_hash = contract.functions.settlement(buyer[agent_b - num_seller], DsoAgentAccount, int(total_pay[day, hour, agent_b]), int(10**6 * total_demand[day, hour, agent_b])).transact() #chech in the SC v6 comments 
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
               
            # We display the buyer's account balance:
            b_en_bal = contract.functions.getbalance(buyer[agent_b - num_seller]).call()
            buyer_en_bal[day][hour][agent_b - num_seller] = b_en_bal
            b_en_bal_eth = w3.from_wei(b_en_bal, "ether")
            buyer_en_bal_eth[day][hour][agent_b - num_seller] = b_en_bal_eth
            #print("Buyer's {0} Energy deposit account Balance (eth): {1}\n".format(agent_b+1, b_en_bal_eth))
             
            # Finally, we convert these energy accounts into real ether by closing everything and redistributing the money 
            #to all the agents
            tx_hash = contract.functions.close(buyer[agent_b - num_seller]).transact()
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
               
            # We display the Buyers' real account balance:
            b_real_bal = contract.functions.getrealbalance(buyer[agent_b - num_seller]).call()
            buyer_real_bal[day][hour][agent_b - num_seller] = b_real_bal
            b_real_bal_eth = w3.from_wei(b_real_bal, "ether")
            buyer_real_bal_eth[day][hour][agent_b - num_seller] = b_real_bal_eth
            print("Real Buyer's {0} account Balance (eth): {1}\n".format(agent_b+1-num_seller, b_real_bal_eth))
   
 
#to see how you will do it for the pros who buy and sell in this round, you could use an if for each case below
        #Seller receives his payment from the dso (the amount corresponding the energy he sold) - the rest is the payment of the dso
        for agent_s in range(num_seller):
           
            if pros_dem_f[day, hour, agent_s] > 0: # pros pay the DSO 
                tx_hash = contract.functions.settlement(seller[agent_s], DsoAgentAccount, int(total_pay[day, hour, agent_s]), int(10**6 * total_demand[day, hour, agent_s])).transact() #chech in the SC v6 comments 
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                  
                # We display the prosumer's account balance:
                sel_en_bal = contract.functions.getbalance(seller[agent_s]).call()
                seller_en_bal[day, hour, agent_s] = sel_en_bal
                sel_en_bal_eth = w3.from_wei(sel_en_bal, "ether")
                seller_en_bal_eth[day, hour, agent_s] = sel_en_bal_eth
                #print("Seller's {0} Energy deposit account Balance (eth): {1}\n".format(agent_s+1, sel_en_bal_eth))
                 
                # Finally, we convert these energy accounts into real ether by closing everything and redistributing the money 
                #to all the agents
                tx_hash = contract.functions.close(seller[agent_s]).transact()
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                # We display the prosumer' real account balance:
                sel_real_bal = contract.functions.getrealbalance(seller[agent_s]).call()
                seller_real_bal[day, hour, agent_s] = sel_real_bal
                sel_real_bal_eth = w3.from_wei(sel_real_bal, "ether")
                seller_real_bal_eth[day, hour, agent_s] = sel_real_bal_eth
                print("Real Seller's {0} account Balance (eth): {1}\n".format(agent_s+1, sel_real_bal_eth))
                  
            elif seller_bidQuantity[day, hour, agent_s] > 0: # pros get paid by DSO
                tx_hash = contract.functions.settlement(DsoAgentAccount, seller[agent_s], int(tot_receive[day, hour, agent_s]), int(10**6 * total_supply[day, hour, agent_s])).transact()
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                   
                # We display the seller's account balance:
                sel_en_bal = contract.functions.getbalance(seller[agent_s]).call()
                seller_en_bal[day, hour, agent_s] = sel_en_bal
                sel_en_bal_eth = w3.from_wei(sel_en_bal, "ether")
                seller_en_bal_eth[day, hour, agent_s] = sel_en_bal_eth
                #print("Seller's {0} Energy deposit account Balance (eth): {1}\n".format(agent_s+1, sel_en_bal_eth))
                 
                # Finally, we convert these energy accounts into real ether by closing everything and redistributing the money 
                #to all the agents
                tx_hash = contract.functions.close(seller[agent_s]).transact()
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                # We display the sellers' real account balance:
                sel_real_bal = contract.functions.getrealbalance(seller[agent_s]).call()
                seller_real_bal[day, hour, agent_s] = sel_real_bal
                sel_real_bal_eth = w3.from_wei(sel_real_bal, "ether")
                seller_real_bal_eth[day, hour, agent_s] = sel_real_bal_eth
                print("Real Seller's {0} account Balance (eth): {1}\n".format(agent_s+1, sel_real_bal_eth))
                
            elif seller_bidQuantity[day, hour, agent_s] == 0 and pros_dem_f[day, hour, agent_s] == 0:
                # prosumer doesn't send or receive any money from DSO
                 
                # We display the seller's account balance:
                sel_en_bal = contract.functions.getbalance(seller[agent_s]).call()
                seller_en_bal[day, hour, agent_s] = sel_en_bal
                sel_en_bal_eth = w3.from_wei(sel_en_bal, "ether")
                seller_en_bal_eth[day, hour, agent_s] = sel_en_bal_eth
                #print("Seller's {0} Energy deposit account Balance (eth): {1}\n".format(agent_s+1, sel_en_bal_eth))
                
                # Finally, we convert these energy accounts into real ether by closing everything and redistributing the money 
                #to all the agents
                tx_hash = contract.functions.close(seller[agent_s]).transact()
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                # We display the sellers' real account balance:
                sel_real_bal = contract.functions.getrealbalance(seller[agent_s]).call()
                seller_real_bal[day, hour, agent_s] = sel_real_bal
                sel_real_bal_eth = w3.from_wei(sel_real_bal, "ether")
                seller_real_bal_eth[day, hour, agent_s] = sel_real_bal_eth
                print("Real Seller's {0} account Balance (eth): {1}\n".format(agent_s+1, sel_real_bal_eth))
            
  
        
        """
        #to check that the energy transactions are kept by the SC correctly
        def get_transaction(index):
            # Call the getter function
            transaction = contract.functions.getTransaction(index).call()
        
            # Unpack the returned tuple
            sender, receiver, energyAmount, verified = transaction
        
            return sender, receiver, energyAmount, verified
    
        # Example usage
        transaction_index = 0
        sender, receiver, energyAmount, verified = get_transaction(transaction_index)
        
        print("Sender:", sender)
        print("Receiver:", receiver)
        print("Energy Amount:", energyAmount)
        print("Verified:", verified)
        """
              
        
        #debug_point_2 = 1

        #The DSO closes the negotiation by taking back the remaining amount from the operational depsosit
        tx_hash = contract.functions.closecontract().transact()
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # We display the Dso's real account balance:
        DSO_bal = w3.eth.get_balance(DsoAgentAccount)
        #print("Real DSO's account Balance (wei): {0}\n".format(DSO_bal))
        DSO_bal_eth = w3.from_wei(DSO_bal, "ether")
        #print("Real DSO's account Balance (eth): {0}\n".format(DSO_bal_eth))
         
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
    
    

     
# End the timer
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time    

# Print the elapsed time
print("Elapsed time: {:.2f} seconds".format(elapsed_time))   
 







