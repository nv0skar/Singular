# Singular
# Copyright (C) 2022 Oscar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from . import declarations
from . import manager
from . import mapping

class formulae:
    @staticmethod
    def calculateReward(transactions=None, forBlock=None):
        """
        Calculate the reward of the miner.
        To calculate the reward the following formula is used:
        Reward = (((((ChainMaxSupply*(2*ChainMaxReward)) / ChainMaxReward) - BlocksMined) / ((ChainMaxSupply*(2*ChainMaxReward)) / ChainMaxReward)) * ChainMaxReward) + CommissionsReward
        (This assumes that the transaction object itself or prepareTransactions() already subtracted 0.01%)
        """
        # Get the transactions or forBlock if one of those are None
        if transactions is None: transactions = manager.manager.memPool.getFromPool()
        if forBlock is None: forBlock = manager.manager.chainMan.getHeight()
        # Check if this is the first block
        if manager.manager.chainMan.getHeight() == 0: return declarations.chainConfig.maxReward
        # Calculate blocks to mine to achieve the max supply
        blocksToMineMaxSupply = int((declarations.chainConfig.maxSupply * (2 * declarations.chainConfig.maxReward)) / declarations.chainConfig.maxReward)
        # Calculate the mining reward
        if not int(forBlock) > int(blocksToMineMaxSupply):
            miningReward = float(((blocksToMineMaxSupply - forBlock) / (blocksToMineMaxSupply)) * declarations.chainConfig.maxReward) if not declarations.chainConfig.testNet else float(blocksToMineMaxSupply * declarations.chainConfig.maxReward)
            # Check if the mining reward exceeds the max reward or the reward its equal or less than 0
            if (miningReward > declarations.chainConfig.maxReward) or (miningReward) <= 0: miningReward = 0
        else: miningReward = 0
        # Get the total generated balance
        generatedBalance = float(float(manager.manager.wallet.getBalance(declarations.chainConfig.rewardName)) * -1)
        # Check if the max supply is exceeded or going to be exceeded
        if float(generatedBalance) > float(declarations.chainConfig.maxSupply): miningReward = 0
        if float(((generatedBalance) + miningReward)) > float(declarations.chainConfig.maxSupply):
            miningReward = float(declarations.chainConfig.maxSupply) - float(generatedBalance)
        # Define the commission rewards
        commissionRewards = 0
        # For unconfirmed transaction was in the memPool get the commission and sum It to commissionRewards
        for trans in transactions:
            if not trans.get(mapping.transactions.amount) <= 0:
                if not trans.get(mapping.transactions.amount) == (trans.get(mapping.transactions.realAmount) - (trans.get(mapping.transactions.realAmount) / 100 * 0.01)):
                    # Remove the invalid transaction from the memPool
                    manager.manager.memPool.removeFromPool(transactionToRemove=trans)
                else: commissionRewards += trans[mapping.transactions.commission]  # Add commission to the commissionRewards
        # Calculate totalReward
        totalReward = float(miningReward + commissionRewards)
        return float(totalReward)

    @staticmethod
    def calculateDifficulty(lastBlockTransactions, lastBlockRealAmount):
        """
        Calculate the difficulty of a block
        To calculate the difficulty of a block the following formula is used:
        Difficulty = (ChainMaxDifficulty/(ChainMaxAmount/(RealAmountOfLastBlock/TransactionsInLastBlock)))
        """
        # If there aren't any blocks return the minDiff
        if manager.manager.chainMan.getHeight() == 0: return int(declarations.miningConfig.minDiff)
        # Calculate the difficulty
        difficulty = int(declarations.miningConfig.maxDiff / (float(declarations.chainConfig.maxAmount) / (float(lastBlockRealAmount) / int(lastBlockTransactions))))
        # Checks If the difficulty is greater than the maximum difficulty established or lower than the minimum difficulty established
        if difficulty < declarations.miningConfig.minDiff: difficulty = declarations.miningConfig.minDiff
        elif difficulty > declarations.miningConfig.maxDiff: difficulty = declarations.miningConfig.maxDiff
        return int(difficulty)
