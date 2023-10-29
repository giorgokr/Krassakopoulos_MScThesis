//this code is less "heavy" than v6 and needs less gas for the transactions to happen

// in this SC the bids in the submit and retrieve bids does not include the bid prices
pragma solidity >=0.4.21 <0.7.0; //compiler used 6.6

contract NegotiationMarketPlace {
    // The Market place stores the count of all the buyers, sellers who sent bids
    uint8 private buyerCount;
    uint8 private sellerCount;
    uint private operationalDeposit; // an amount of money used to pay all operation fees

    // The market place stores (with a hash) the bid (price and quantity, we also need the weights (or Beta) and other informations to be added), and 
    //the type of the agent (Buyer (1) or Seller (0))
    mapping (address => uint) private bidQuantity;
    mapping (address => uint) public agentType;
    mapping (address => uint) private depositAmount;

    struct EnergyTransaction {
        address sender;
        address receiver;
        uint energyAmount;
        bool verified;
    }

    EnergyTransaction[] public transactions;

    // The market place is owned by the DSO Agent:
    address payable public dsoAgent;

    // We need  a boolean to state the stage of the market place (open or not for receiving new offers/bids) Set to true at the end, disallows any change.
    // By default initialized to `false`. By default, if no value is assigned, the boolean variable is initialized to false.
    bool ended;

    //  We create a modifier that could be used later to restrict some functions to only the operator. not needed for simple use
    modifier onlyOperator() {
        require(
            msg.sender == dsoAgent,
            "Only DSO/Operator can call this."
        );
        _;
    }

    // Constructor function to initialize the MarketPlace. It is "payable" so it can receive initial funding to cover up some mispayment
    constructor() public payable {
       // require(msg.value == 10 ether, "10 ether initial funding required");
        /* Set the owner to the creator of this contract */
        dsoAgent = msg.sender;
        //This line assigns the address of the sender of the contract creation transaction to the dsoAgent variable. 
        //msg.sender refers to the Ethereum address of the account that deployed the contract.

        // initialization of variables
        buyerCount = 0;
        sellerCount = 0;
    }


    // used to refill the amount of the operational deposit
    function operationaldeposit() public payable onlyOperator returns (uint) { 
    //"payable": This keyword indicates that the function can receive Ether. It allows the function to accept funds along with the function .call()
    //"returns (uint)": This part specifies the return type of the function. In this case, it returns an unsigned integer (uint).

        operationalDeposit = operationalDeposit + msg.value; // adding the value sent with the function call (msg.value). msg.value represents the 
          //amount of Ether sent along with the function call.

         return 1; //This statement returns the value 1 of type uint as the result of the function execution.
    }


    ///  Creation of a bid from an agent return The type of the agent (1 or 0)
    function submitBid(uint _bidquantity, uint _agenttype) public payable  returns (uint) {
       if (_agenttype == 1) {
            buyerCount++;}
        else  {
            sellerCount++;
        }
        // We update all values of this agent - it updates the values for this specific account? how it knows which account? with the msg.sender? 
        // isn't msg.sender the dso?
        bidQuantity[msg.sender] = _bidquantity;
        agentType[msg.sender] = _agenttype;
        depositAmount[msg.sender] = msg.value;

         return agentType[msg.sender];
    }

 // this function I guess that returns the eth deposit (depositAmount) made by account address
  function getbalance(address agentaddress) public view returns(uint) {
        uint out;
        out = depositAmount[agentaddress];
        return out;
    }

 // this function I guess that returns the eth left balance in that account address
  function getrealbalance(address agentaddress) public view returns(uint) {
        uint out;
            if (agentaddress!=dsoAgent){
                out = agentaddress.balance;
            }
            else
            {
                out = dsoAgent.balance;
            }
        return out;
    }

// The operator or DSO wants to retrieve all the bids. However, mapping does not allow to do that. Hence, we can either store each bid/agent into an 
//iterable mapping or the operator/DSO makes as many requests to this Smart Contract to retrieve all the bids from all the registered agents. 
//And if an agent has not placed a bid, it returns 0

    function retrievebid(address agentaddress) public view returns(uint[3] memory) {  // we store the return into memory, not storage, as we do not 
     //need it outside of the function 
        require(msg.sender == dsoAgent,"Only DSO/Operator can call this.");
        uint[3] memory array;
            array = [bidQuantity[agentaddress],agentType[agentaddress],depositAmount[agentaddress]];
            return array;
        

    }

  function settlement(address senderAddress, address payable receivAddress, uint pay_price, uint energyAmount) external onlyOperator {
        if (depositAmount[senderAddress]>pay_price){
            // selleraddress.transfer(pricetopay); // we transfer the money to the seller
            depositAmount[receivAddress] = depositAmount[receivAddress] + pay_price; // we update the seller's deposit amount in this SC
            depositAmount[senderAddress] = depositAmount[senderAddress] - pay_price;// we update the buyer's deposit amount in this SC
            //these amounts are added or taken to and from the deposit acounts of the sellers and the buyers
        
            transactions.push(EnergyTransaction(receivAddress, senderAddress, energyAmount, true));
            // It represents an energy transfer from receiverAddress to the senderAddress  with a specific energyAmount 
            //and sets the verified flag to true.

        
        }
    }
 
// Once everything is finished, the DSO/operator close the negotiation by redistributing the money that is in the accounts
  function close(address payable agentaddress) external payable onlyOperator {
            if (agentaddress!=dsoAgent){
            agentaddress.transfer(depositAmount[agentaddress]); // we transfer the money to the sellers or buyers real eth acount
            }
            else
            {
                dsoAgent.transfer(operationalDeposit); // we transfer the operational deposit money back to the DSO
            }
    }
 

}
