// in this SC the bids in the submit and retrieve bids does not include the bid prices
pragma solidity >=0.4.21 <0.7.0; //compiler used 6.6

contract NegotiationMarketPlace {
    // The Market place stores the count of all the buyers, sellers who sent bids
    uint8 private buyerCount;
    uint8 private sellerCount;
    uint private operationalDeposit; // an amount of money used to pay all operation fees


    // The market place stores (with a hash) the bid (price and quantity, we also need the weights (or Beta) and other informations to be added), and 
    //the type of the agent (Buyer (1) or Seller (0))
    //mapping (address => uint) private bidPrice;
    mapping (address => uint) private bidQuantity;
    mapping (address => uint) private bidWeight;
    mapping (address => uint) public agentType;
    mapping (address => uint) private depositAmount;

    struct EnergyTransaction {
        address sender;
        address receiver;
        uint energyAmount;
        bool verified;
    }

    EnergyTransaction[] public transactions;

    //If we use state machine to coordinate all steps
    enum State { BID_DEPOSIT_OPEN, BID_DEPOSIT_OVER, AWAITING_DELIVERY, COMPLETE, FINISHED}
    State public currState; // the value of the state enum each time will be stored in "currState" variable

    // The market place is owned by the DSO Agent:
    address payable public dsoAgent;
     
    // We also need to add a time: Times are either absolute unix timestamps (seconds since 1970-01-01) or time periods in seconds.
    uint public marketEndTime; // not used yet

    // Log the event about a bid being made by an address (Agent) and its amount
    event LogBidMade(address indexed accountAddress, uint quantity, uint Weight); // Notice that weights
    // are uint for now, as fixed point are not yet fully implemented (=> the DSO will divide by 10)
    event LogEnergyTransferred(address indexed sender, address indexed receiver, uint energyAmount);

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
    function submitBid(uint _bidquantity, uint _bidweight, uint _agenttype) public payable  returns (uint) {
         // if we use state machine, require(currState == State.BID_DEPOSIT_OPEN, "Cannot confirm Bid deposit");
       if (_agenttype == 1) {
            buyerCount++;}
        else  {
            sellerCount++;
        }
        // We update all values of this agent - it updates the values for this specific account? how it knows which account? with the msg.sender? 
        // isn't msg.sender the dso?
        //bidPrice[msg.sender] = _bidprice;
        bidQuantity[msg.sender] = _bidquantity;
        bidWeight[msg.sender] = _bidweight;
        agentType[msg.sender] = _agenttype;
        depositAmount[msg.sender] = msg.value;
         // if (timesup ***** or agent count reached) currState = State.BID_DEPOSIT_OVER;

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

    function retrievebid(address agentaddress) public view returns(uint[4] memory) {  // we store the return into memory, not storage, as we do not 
     //need it outside of the function
     //the "uint[5]": specifies the return type of the function, which is an array of unsigned integers (uint) with a fixed size of 4. 
        require(msg.sender == dsoAgent,"Only DSO/Operator can call this.");
        // if we use state machine, require(currState == State.BID_DEPOSIT_OVER, "Cannot confirm Bid deposit");
        uint[4] memory array;
        //if (bidPrice[agentaddress] != 0){
            array = [bidQuantity[agentaddress],bidWeight[agentaddress],agentType[agentaddress],depositAmount[agentaddress]];
        //}
            return array;
         //currState = State.AWAITING_DELIVERY;

    }

  function settlement(address senderAddress, address payable receivAddress, uint pay_price, uint energyAmount) external onlyOperator {
        // if we use state machine, require(currState == State.AWAITING_DELIVERY, "Cannot confirm delivery");
        if (depositAmount[senderAddress]>pay_price){
            // selleraddress.transfer(pricetopay); // we transfer the money to the seller
            depositAmount[receivAddress] = depositAmount[receivAddress] + pay_price; // we update the seller's deposit amount in this SC
            depositAmount[senderAddress] = depositAmount[senderAddress] - pay_price;// we update the buyer's deposit amount in this SC
            //these amounts are added or taken to and from the deposit acounts of the sellers and the buyers
        
            transactions.push(EnergyTransaction(receivAddress, senderAddress, energyAmount, true));
            // It represents an energy transfer from receiverAddress to the senderAddress  with a specific energyAmount 
            //and sets the verified flag to true.

            //emit LogEnergyTransferred(senderAddress, receivAddress, energyAmount);
        
        }
        //currState = State.COMPLETE;
    }
 
// Once everything is finished, the DSO/operator close the negotiation by redistributing the money that is in the accounts
  function close(address payable agentaddress) external payable onlyOperator {
        // if we use state machine, require(currState == State.COMPLETE, "Cannot confirm delivery");
            // selleraddress.transfer(depositAmount[selleraddress]); // we transfer the money to the seller
            if (agentaddress!=dsoAgent){
            agentaddress.transfer(depositAmount[agentaddress]); // we transfer the money to the sellers or buyers real eth acount
            }
            else
            {
                dsoAgent.transfer(operationalDeposit); // we transfer the operational deposit money back to the DSO
            }
        //currState = State.FINISHED;
    }

    // Once everything is finished, the DSO/operator close the negotiation by redistributing the money that is in the accounts
  function closecontract() external payable onlyOperator {
        // if we use state machine, require(currState == State.COMPLETE, "Cannot confirm delivery");
            // selleraddress.transfer(depositAmount[selleraddress]); // we transfer the money to the seller
            uint fee;
            fee = 1;  // we define is a fee of operational cost that should be removed...
                msg.sender.transfer(operationalDeposit-fee); // if I remove it then the DSO will have no losses in money
        //currState = State.FINISHED;
    }

   /* 
   function verifyTransaction(uint transactionIndex) external {
        require(transactionIndex < transactions.length, "Invalid transaction index");
        require(transactions[transactionIndex].sender == msg.sender, "You can only verify your own transactions");
        
        transactions[transactionIndex].verified = true;
    } 
    */

    function getTransaction(uint index) public view returns (address, address, uint, bool) {
        require(index < transactions.length, "Invalid transaction index");
        
        EnergyTransaction storage transaction = transactions[index];
        
        return (transaction.sender, transaction.receiver, transaction.energyAmount, transaction.verified);
    }
 

}



/*  // The following comment is a so-called natspec comment, recognizable by the three slashes. It will be shown when the user is asked to confirm a transaction.
    /// Create a simple MarketPlace with `_marketEndTime` seconds bidding time 
    constructor(
        uint _marketEndTime,
   //     address payable _beneficiary
    ) public {
     //   beneficiary = _beneficiary;
        marketEndTime = now + _marketEndTime;
    } 
    */
