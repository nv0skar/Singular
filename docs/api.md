# Using the Web API
When interacting with the Web API the addresses should be sent in base16 🙏
### <a name="webAPIMain"></a>`/`
Get info about the node
- **Method:** GET
- **Status code:** 200 - OK
- **Response type:** Json
- **Response structure:** 
```json
{
  "network": "Here should be the network name of the node", 
  "networkMagicID": "Here should be the magic number of the network",
  "protocolVersion": "Here should be the protocol version of the node", 
  "agent": "Here should be the info of the node"
}
```
- **Response example:**
```json
{ 
  "network": "mainSpace", 
  "networkMagicID": "tLnAENVf5oN59ZcfCCPWShmzhLdgNvHZ1eib",
  "protocolVersion": "1",
  "agent": "SingularNode@v1"
}
```

## <a name="webAPIWallet"></a>Wallet
### <a name="webAPIBalance"></a>`/wallet/balance/<wallet>`
Get the balance of an address
- **Method:** GET
- **Status code:** 200 - OK
- **Response type:** Json
- **Response structure:** 
```json
{
  "address": "Here should be the address of the requested balance holder", 
  "balance": Here should be the balance of the wallet address
}
```
- **Response example:**
```json
{
  "address": "RandomMiner", 
  "balance": 58.6
}
```

### <a name="webAPITransactions"></a>`/wallet/transactions/<wallet>`
Get the transactions of a given address
- **Method:** GET
- **Status code:** 200 - OK
- **Response type:** Json
- **Response structure:** 
```json
{
  "address": "Here should be the address of the requested balance holder", 
  "transactions": Here should be the transactions of an address
}
```
- **Response example:**
```json
{
  "address": "RandomMiner", 
  "transactions": [
    {
      "amount": 19.998, 
      "commission": 0.002, 
      "realAmount": 20.0, 
      "receiver": "SuperMiner", 
      "sender": "RandomMiner", 
      "signature": "Some signature here", 
      "time": 4102444799.0
    }
  ]
}
```

### <a name="webAPIIssue"></a>`/wallet/issue`
Get the transactions of a given address
- **Method:** POST
- **Status code:** 200 - OK | 400-FAILED
- **Message type:** Json
- **Message structure:**
```json
{
  "sender": "Here should be the address of the sender", 
  "receiver": "Here should be the addressod the receiver",
  "realAmount": Here should be the amount to send,
  "signature": "Here should be the signature of the request",
  "time": "Here should be the time of the request"
}
```
- **Message example:**
```json
{
  "sender": "RandomMiner", 
  "receiver": "SuperMiner",
  "realAmount": 20.0,
  "signature": "Some signature here",
  "time": 4102444799.0
}
```
- **Response type:** Json
- **Response structure:** 
```json
{
  "status": "Here should be info indicating if the transaction was failed or successful", 
  "reason": "Here should be the reason why"
}
```
- **Response example:** 
```json
When status code is 200:

  {
    "status": "success", 
    "reason": "Here should be the reason why"
  }

When status code is 400:

  {
    "status": "failed", 
    "reason": "Here should be the reason why"
  }
```
