# Transactions
### <a name="transactionsObtainingTransaction"></a>Obtaining transaction info
This is the structure of a transaction returned from a node.

The content is:
- **Amount (amount):** The amount that the receiver will get.
- **Commission (commision):** The amount that is extracted from the real amount sent.
- **Real amount (realAmount):** The amount that is sent by the sender.
- **Receiver (receiver):** The address who is going to receive.
- **Sender (sender):** The address who is going to send.
- **Signature (signature):** The signature of the transaction
- **Time (time):** The time when the transaction was issued

Example:
```json
{
  "amount": 19.998, 
  "commission": 0.002, 
  "realAmount": 20.0, 
  "receiver": "SuperMiner", 
  "sender": "RandomMiner", 
  "signature": "Some signature here", 
  "time": 4102444799.0
}
```
### <a name="transactionsSigningTransaction"></a>Signing a transaction
1. Firstly, you have to generate a private key and a public key using the `Ed25519` algorithm.

2. Then, calculate the amount from the real amount using this formula:

	**realAmount - ((realAmount / 100) * 0.01)**

3. After that, sign the transaction following this format:
```
(senderAddressInBase16-receiverAddressInBase16-realAmount-amount)@currentTime

Example:

(RandomMiner-SuperMiner-20.0-19.998)@4102444799.0

```

4. Lastly, encode the signature into base16.

### <a name="transactionsComposingTransaction"></a>Composing a transaction to be sent
This is the structure to follow to send a transaction to a node.

- **Real amount (realAmount):** The amount that is sent by the sender.
- **Receiver (receiver):** The address who is going to receive.
- **Sender (sender):** The address who is going to send.
- **Signature (signature):** The signature of the transaction
- **Time (time):** The time when the transaction was issued
```json
{
  "sender": "RandomMiner", 
  "receiver": "SuperMiner",
  "realAmount": 20.0,
  "signature": "Some signature here",
  "time": 4102444799.0
}
```
