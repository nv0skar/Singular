# Formulae
## <a name="formulaeCalculatingReward"></a> Calculating miner reward
When a miner finishes the mine of a block a reward should be issued there are two forms of reward:
1. **Reward from the balance generator**: This is issued in order to reach the max supply of the chain.
2. **Reward from commissions**: This is issued in order to guarantee that the miner still has a reward even if the reward from the balance generator is over.

Finally when both are calculated, they are combined to form the mining reward, except when the max supply is reached, if that is the case, only the commission reward will be added because no supply is left.

### <a name="formulaeCalculatingRewardChain"></a> Calculating reward and balance to generate
To calculate the reward and balance you have to generate you have to use the following formula:

```
(((((x*(2y)) / y) - z) / ((x*(2y)) / y)) * y)
```

Where:
- `x` is the chain's max supply
- `y` is chain's max reward
- `z` is number of blocks mined


### <a name="formulaeCalculatingRewardCommission"></a> Calculating reward from commissions
To calculate the reward from commissions you have to get the real amount sent by each transaction and substract 0.01% of itself, then you will get the amount that is received by the the receiver.

```
(x/100)*(0.01x)
```

Where:
- `x` is the number of transactions


## <a name="formulaeCalculatingBlockDifficulty"></a> Calculating block difficulty
In order to calculate the difficulty we have to use the following formula:
```
(x/(y/(z/w)))
```

Where:
- `x` is the maximum difficulty established
- `y` is the chain max amount
- `z` is the real amount sent in the last block
- `w` are the transactions issued in the last block

There are different conditions that affects the final difficulty. These conditions are:
- If the difficulty is greater than the maximum difficulty established, the difficulty will be the maximum difficulty established.
- If the difficulty is lower than the minimum difficulty established, the difficulty will be the minimum difficulty established.

