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
#This code .v24 is used only to estimate the gas of the functions calling the SC in .v23


##SOS note##
#When interacting with a smart contract on the Ethereum network, the account that initiates the transaction 
#is responsible for paying the gas fee.

  
#import time 
import json
from web3 import Web3
#from Price_to_Pay_v5 import price
#from avePrice_year import avePrice_0 
#import random
#import matplotlib.pyplot as plt
import numpy as np

# Start the timer
#start_time = time.time() 
 
def deploy_contract(w3, contract_interface):
    tx_hash = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
        ).constructor().transact()
        #functions.transact() executes the specified function by sending a new public transaction.
    address = w3.eth.wait_for_transaction_receipt(tx_hash)['contractAddress']
    return address

ether = 10**18 # 1 ether = 1000000000000000000 wei

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
num_hours = 2
num_seller = 3 # declare the number of sellers
num_buyer = 3 # declare the number of buyers

seller = np.zeros((num_seller), dtype = object)
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


# Deployment of the contract
address = deploy_contract(w3, contract_interface)

contract = w3.eth.contract(
    address = address,
    abi = abi
)


# Estimate gas for contract deployment
SC_depl_GAS = w3.eth.contract(
    abi=contract_interface['abi'],
    bytecode=contract_interface['bin']
).constructor().estimate_gas()


#function I call from the SC and their state:
# operationaldeposit() -> state-changing
#submitBid() -> state-changing
#retrievebid() -> read-only
#getbalance() -> read-only
#settlement() -> state-changing 
#close() -> state-changing 
#getrealbalance() -> read-only
#closecontract() -> state-changing 
#getTransaction() -> read-only   
 

 
#Estimate gas for the operational deposit by the DSO is being made
"""
tx = { 
 # dictionary with the info of the transaction that we will make -- for details what each of them means look web3 from yt _tut3 
 #python code file
   'from': DsoAgentAccount,
   'to': address,
   'value': w3.to_wei(1,'ether'),
   'gas': 2000000,
   'gasPrice': w3.to_wei('20','gwei'),
 }
"""

GAS_DSO_depo = contract.functions.operationaldeposit().estimate_gas()

# Estimate gas for the transaction
#gas_estimate = function.estimate_gas(tx)
  
 
#estimate gas for the submit bid by the pros - seller
GAS_prosSELL_submitBID = contract.functions.submitBid(1, 1, 0).estimate_gas()
#SB_2 = contract.functions.submitBid().estimate_gas() #this doesn't work, it needs parameters in the function like in SB_pros

#estimate gas for the submit bid by the pros - buyer 
#it's higher than the GAS_prosSELL_submitBID, because now agent_type = 0, as he buyes energy  
GAS_prosBUY_submitBID = contract.functions.submitBid(1, 1, 1).estimate_gas()

#estimate gas for the submit bid by the cons - buyer 
GAS_consBUY_submitBID = contract.functions.submitBid(1, 1, 1).estimate_gas()

# est gas for the retrieve of the pros-sellers' bids for that hour of the day
GAS_prosSELL_retreive = contract.functions.retrievebid(seller[0]).estimate_gas()
 
# est gas for the retrieve of the prosumer-Buyer's bid
GAS_prosBUY_retreive = contract.functions.retrievebid(seller[0]).estimate_gas() 

# est gas for the retrieve of the consumer-Buyer's bid
GAS_consBUY_retreive = contract.functions.retrievebid(buyer[0]).estimate_gas()
  
# est gas to get the deposit balance of the  the pros-sellers' account:
GAS_prosSELL_depo = contract.functions.getbalance(seller[0]).estimate_gas() 

# est gas to get the deposit balance of the  the pros-buyers' account: 
GAS_prosBUY_depo = contract.functions.getbalance(seller[0]).estimate_gas() 

# est gas to get the deposit balance of the  the cons-buyers' account: 
GAS_consBUY_depo = contract.functions.getbalance(buyer[0]).estimate_gas() 



############
#for the payments - estimate gas, below:

#est gas for the Payments by consumer-buyers to DSO    
# est gas of the transaction of the cons-buyer sending funds to DSO 
GAS_consBUY_send = contract.functions.settlement(buyer[0], DsoAgentAccount, ether, int(10**6 * 1)).estimate_gas() 
 
# est gas to get for second time after sending funds, the deposit balance of the  the cons-buyers' account: 
GAS_consBUY_depo2 = contract.functions.getbalance(buyer[0]).estimate_gas()

# est gas to convert the deposit accounts into real ether by closing everything and redistributing the money to cons-buyers
GAS_consBUY_close = contract.functions.close(buyer[0]).estimate_gas()

# est gas to get the real account balance of the  the cons-buyers' account, after the auction is over: 
GAS_consBUY_bal = contract.functions.getrealbalance(buyer[0]).estimate_gas()  


#est gas for the Payments by prosumer-buyers to DSO    
# est gas of the transaction of the pros-buyer sending funds to DSO 
GAS_prosBUY_send = contract.functions.settlement(seller[0], DsoAgentAccount, ether, int(10**6 * 1)).estimate_gas() 
  
# est gas to get for second time after sending funds, the deposit balance of the  the pros-buyers' account: 
GAS_prosBUY_depo2 = contract.functions.getbalance(seller[0]).estimate_gas()

# est gas to convert the deposit accounts into real ether by closing everything and redistributing the money to pros-buyers
GAS_prosBUY_close = contract.functions.close(seller[0]).estimate_gas()
 
# est gas to get the real account balance of the  the pros-buyers' account, after the auction is over: 
GAS_prosBUY_bal = contract.functions.getrealbalance(seller[0]).estimate_gas()


#est gas for the Payments by DSO to prosumer-sellers
# est gas of the transaction of the DSO sending funds to pros-seller
GAS_DSO_send = contract.functions.settlement(DsoAgentAccount, seller[0], ether, int(10**6 * 1)).estimate_gas() 
  
# est gas to get for second time after sending funds, the deposit balance of the  the pros-sellers' account: 
GAS_prosSELL_depo2 = contract.functions.getbalance(seller[0]).estimate_gas()
 
# est gas to convert the deposit accounts into real ether by closing everything and redistributing the money to pros-sellers
GAS_prosSELL_close = contract.functions.close(seller[0]).estimate_gas()
 
# est gas to get the real account balance of the  the pros-sellers' account, after the auction is over: 
GAS_prosSELL_bal = contract.functions.getrealbalance(seller[0]).estimate_gas()


#est gas for the prosumer who neither send or receive ETH in that round
  
# est gas to get for second time after sending funds, the deposit balance of the prosNEUTRAL account: 
GAS_prosNEUTRAL_depo2 = contract.functions.getbalance(seller[0]).estimate_gas()
 
# est gas to convert the deposit accounts into real ether by closing everything and redistributing the money to prosNEUTRAL
GAS_prosNEUTRAL_close = contract.functions.close(seller[0]).estimate_gas()
 
# est gas to get the real account balance of the  the prosNEUTRAL account, after the auction is over: 
GAS_prosNEUTRAL_bal = contract.functions.getrealbalance(seller[0]).estimate_gas() 
 

#DSO closes the contract

#est gas for the DSO closes the negotiation by taking back the remaining amount from the operational depsosit
#GAS_DSO_closeContract = contract.functions.closecontract().estimate_gas() 
GAS_DSO_closeContract = contract.functions.close(DsoAgentAccount).estimate_gas() 
 
# est gas to realocate funds from the deposit to the Dso's real account balance:
#GAS_DSO_finalBal = w3.eth.get_balance(DsoAgentAccount).estimate_gas() 
GAS_DSO_finalBal = contract.functions.getrealbalance(DsoAgentAccount).estimate_gas() 
 



#lists containing the gas units created the pros-seller 
#the ones that come from read-only functions do not need to be paid 
#the get_balance function are read only and do not cost any gas
LIST_prosSELL = [("submit bid", GAS_prosSELL_submitBID), 
                 ("retrieve bid", GAS_prosSELL_retreive), 
                 ("get deposit balance 1", GAS_prosSELL_depo), 
                 ("get deposit balance 2", GAS_prosSELL_depo2), 
                 ("close - reallocate funds", GAS_prosSELL_close),
                 ("real end auction balance", GAS_prosSELL_bal)] 


#lists containing the gas units created the pros-buyer - the get_balance function are read only 
#and do not cost any gas 
LIST_prosBUY = [("submit bid", GAS_prosBUY_submitBID), 
                 ("retrieve bid", GAS_prosBUY_retreive), 
                 ("get deposit balance 1", GAS_prosBUY_depo),
                 ("settlement - pay DSO", GAS_prosBUY_send),
                 ("get deposit balance 2", GAS_prosBUY_depo2), 
                 ("close - reallocate funds", GAS_prosBUY_close),
                 ("real end auction balance", GAS_prosBUY_bal)] 

 
#lists containing the gas units created the pros-NEUTRAL - the get_balance function are read only 
#and do not cost any gas  
LIST_prosNEUTRAL = [("submit bid", GAS_prosSELL_submitBID), 
                     ("retrieve bid", GAS_prosSELL_retreive), 
                     ("get deposit balance 1", GAS_prosSELL_depo), 
                     ("get deposit balance 2", GAS_prosNEUTRAL_depo2), 
                     ("close - reallocate funds", GAS_prosNEUTRAL_close),
                     ("real end auction balance", GAS_prosNEUTRAL_bal)]


#lists containing the gas units created the cons-buyer - the get_balance function are read only 
#and do not cost any gas  
LIST_consBUY = [("submit bid", GAS_consBUY_submitBID), 
                 ("retrieve bid", GAS_consBUY_retreive), 
                 ("get deposit balance 1", GAS_consBUY_depo),
                 ("settlement - pay DSO", GAS_consBUY_send ),
                 ("get deposit balance 2", GAS_consBUY_depo2), 
                 ("close - reallocate funds", GAS_consBUY_close),
                 ("real end auction balance", GAS_consBUY_bal)]


#lists containing the gas units created the DSO - the get_balance function are read only 
#and do not cost any gas    
LIST_DSO = [("send operational deposit", GAS_DSO_depo), 
            ("DSO pays pros-seller", GAS_DSO_send),   
            ("close - reallocate funds", GAS_DSO_closeContract),
            ("real end auction balance", GAS_DSO_finalBal)]  




###########################################################
###########
#lists containing the gas units ONLY need to be paid by the pros-seller
ETH_2_EURO = 1612.9032 # equivalent eth to euro - 1 eth = 1612.9032 euro 
unitGas_cost = 30 # cost per unit of gas in GWEI as of 11/07/2023 
sumGas_prosSELL = GAS_prosSELL_submitBID + GAS_prosSELL_close
totalGas_cost_GWEI_prosSELL = unitGas_cost * sumGas_prosSELL # total cost of all gas in GWEI
totalGas_cost_WEI_prosSELL = w3.to_wei(totalGas_cost_GWEI_prosSELL,'gwei') # total cost of all gas in WEI
totalGas_cost_ETH_prosSELL = w3.from_wei(totalGas_cost_WEI_prosSELL,'ether') # total cost of all gas in ETH
totalGas_cost_EURO_prosSELL = float(totalGas_cost_ETH_prosSELL) * ETH_2_EURO # total cost of all gas in EURO
 
a = 5500000
totalGas_cost_GWEI_a = unitGas_cost * a # total cost of all gas in GWEI
totalGas_cost_WEI_a = w3.to_wei(totalGas_cost_GWEI_a,'gwei') # total cost of all gas in WEI
totalGas_cost_ETH_a = w3.from_wei(totalGas_cost_WEI_a,'ether') # total cost of all gas in ETH
totalGas_cost_EURO_a = float(totalGas_cost_ETH_a) * ETH_2_EURO


PAYgas_prosSELL = [("submit bid", GAS_prosSELL_submitBID),   
                   ("close - reallocate funds", GAS_prosSELL_close),
                   ("Gas sum", sumGas_prosSELL),
                   ("gasPrice in GWEI", totalGas_cost_GWEI_prosSELL),
                   ("gasPrice in WEI", totalGas_cost_WEI_prosSELL),
                   ("gasPrice in ETH", float(totalGas_cost_ETH_prosSELL)),
                   ("gasPrice in EURO", totalGas_cost_EURO_prosSELL)] 
  
 
#lists containing the gas units ONLY need to be paid by the pros-buyer
sumGas_prosBUY = GAS_prosBUY_submitBID + GAS_prosBUY_send + GAS_prosBUY_close
totalGas_cost_GWEI_prosBUY = unitGas_cost * sumGas_prosBUY # total cost of all gas in GWEI
totalGas_cost_WEI_prosBUY = w3.to_wei(totalGas_cost_GWEI_prosBUY,'gwei') # total cost of all gas in WEI
totalGas_cost_ETH_prosBUY = w3.from_wei(totalGas_cost_WEI_prosBUY,'ether') # total cost of all gas in ETH
totalGas_cost_EURO_prosBUY = float(totalGas_cost_ETH_prosBUY) * ETH_2_EURO # total cost of all gas in EURO

PAYgas_prosBUY = [("submit bid", GAS_prosBUY_submitBID),  
                  ("settlement - pay DSO", GAS_prosBUY_send), 
                  ("close - reallocate funds", GAS_prosBUY_close),
                  ("Gas sum", sumGas_prosBUY),
                  ("gasPrice in GWEI", totalGas_cost_GWEI_prosBUY),
                  ("gasPrice in WEI", totalGas_cost_WEI_prosBUY),
                  ("gasPrice in ETH", float(totalGas_cost_ETH_prosBUY)),
                  ("gasPrice in EURO", totalGas_cost_EURO_prosBUY)] 
                    
#lists containing the gas units ONLY need to be paid by the pros-NEUTRAL 
sumGas_prosNEUTRAL = GAS_prosSELL_submitBID + GAS_prosNEUTRAL_close 
totalGas_cost_GWEI_prosNEUTRAL = unitGas_cost * sumGas_prosNEUTRAL # total cost of all gas in GWEI
totalGas_cost_WEI_prosNEUTRAL = w3.to_wei(totalGas_cost_GWEI_prosNEUTRAL,'gwei') # total cost of all gas in WEI
totalGas_cost_ETH_prosNEUTRAL = w3.from_wei(totalGas_cost_WEI_prosNEUTRAL,'ether') # total cost of all gas in ETH
totalGas_cost_EURO_prosNEUTRAL = float(totalGas_cost_ETH_prosNEUTRAL) * ETH_2_EURO # total cost of all gas in EURO
  
PAYgas_prosNEUTRAL = [("submit bid", GAS_prosSELL_submitBID),  
                      ("close - reallocate funds", GAS_prosNEUTRAL_close),
                      ("Gas sum", sumGas_prosNEUTRAL),
                      ("gasPrice in GWEI", totalGas_cost_GWEI_prosNEUTRAL),
                      ("gasPrice in WEI", totalGas_cost_WEI_prosNEUTRAL),
                      ("gasPrice in ETH", float(totalGas_cost_ETH_prosNEUTRAL)),
                      ("gasPrice in EURO", totalGas_cost_EURO_prosNEUTRAL)]


#lists containing the gas units ONLY need to be paid by the cons-buyer
sumGas_consBUY = GAS_consBUY_submitBID + GAS_consBUY_send + GAS_consBUY_close
totalGas_cost_GWEI_consBUY = unitGas_cost * sumGas_consBUY # total cost of all gas in GWEI
totalGas_cost_WEI_consBUY = w3.to_wei(totalGas_cost_GWEI_consBUY,'gwei') # total cost of all gas in WEI
totalGas_cost_ETH_consBUY = w3.from_wei(totalGas_cost_WEI_consBUY,'ether') # total cost of all gas in ETH
totalGas_cost_EURO_consBUY = float(totalGas_cost_ETH_consBUY) * ETH_2_EURO # total cost of all gas in EURO
 
PAYgas_consBUY = [("submit bid", GAS_consBUY_submitBID), 
                 ("settlement - pay DSO", GAS_consBUY_send ),
                 ("close - reallocate funds", GAS_consBUY_close),
                 ("Gas sum", sumGas_consBUY),
                 ("gasPrice in GWEI", totalGas_cost_GWEI_consBUY),
                 ("gasPrice in WEI", totalGas_cost_WEI_consBUY),
                 ("gasPrice in ETH", float(totalGas_cost_ETH_consBUY)),
                 ("gasPrice in EURO", totalGas_cost_EURO_consBUY)]
 

#lists containing the gas units ONLY need to be paid by the DSO
sumGas_DSO = GAS_DSO_depo + GAS_DSO_send + GAS_DSO_closeContract
totalGas_cost_GWEI_DSO = unitGas_cost * sumGas_DSO # total cost of all gas in GWEI
totalGas_cost_WEI_DSO = w3.to_wei(totalGas_cost_GWEI_DSO,'gwei') # total cost of all gas in WEI
totalGas_cost_ETH_DSO = w3.from_wei(totalGas_cost_WEI_DSO,'ether') # total cost of all gas in ETH
totalGas_cost_EURO_DSO = float(totalGas_cost_ETH_DSO) * ETH_2_EURO # total cost of all gas in EURO
 
PAYgas_DSO = [("send operational deposit", GAS_DSO_depo), 
                ("DSO pays pros-seller", GAS_DSO_send),   
                ("close - reallocate funds", GAS_DSO_closeContract), 
                ("Gas sum", sumGas_DSO),
                ("gasPrice in GWEI", totalGas_cost_GWEI_DSO),
                ("gasPrice in WEI", totalGas_cost_WEI_DSO),
                ("gasPrice in ETH", float(totalGas_cost_ETH_DSO)),
                ("gasPrice in EURO", totalGas_cost_EURO_DSO)] 

  
#lists containing the gas units ONLY need to be paid for the contract deployment 
sumGas_SC_deploy = SC_depl_GAS
totalGas_cost_GWEI_SC_deploy = unitGas_cost * sumGas_SC_deploy # total cost of all gas in GWEI
totalGas_cost_WEI_SC_deploy = w3.to_wei(totalGas_cost_GWEI_SC_deploy,'gwei') # total cost of all gas in WEI
totalGas_cost_ETH_SC_deploy = w3.from_wei(totalGas_cost_WEI_SC_deploy,'ether') # total cost of all gas in ETH
totalGas_cost_EURO_SC_deploy = float(totalGas_cost_ETH_SC_deploy) * ETH_2_EURO # total cost of all gas in EURO
 
PAYgas_SC_deploy = [("Initial Contract Deployment", SC_depl_GAS), 
                ("Gas sum", SC_depl_GAS),
                ("gasPrice in GWEI", totalGas_cost_GWEI_SC_deploy),
                ("gasPrice in WEI", totalGas_cost_WEI_SC_deploy),
                ("gasPrice in ETH", float(totalGas_cost_ETH_SC_deploy)),
                ("gasPrice in EURO", totalGas_cost_EURO_SC_deploy)]

   
#function I call from the SC and their state:
#operationaldeposit() -> state-changing
#submitBid() -> state-changing
#settlement() -> state-changing
#close() -> state-changing  
#closecontract() -> state-changing 

#retrievebid() -> read-only
#getbalance() -> read-only
#getrealbalance() -> read-only
#getTransaction() -> read-only  


#save also gas from contract deployment











 







