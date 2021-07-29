# Singular
# Copyright (C) 2021 ItsTheGuy
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

class Formulae:
    @staticmethod
    def calculateReward(transactions=None, forBlock=None):
        """
        Calculate the reward of the miner.
        To calculate the reward the following algorithm Is used:
        Reward = (((((BlockMaxSupply*2) / BlockMaxReward) - BlocksMined / ((BlockMaxSupply*2) / BlockMaxReward)) * BlockMaxReward) + commissionRewards
        (This assumes that the transaction object itself or prepareTransactions() already subtracted 0.01%)
        """
        # Get the transactions or forBlock if one of those are None
        if transactions is None: transactions = manager.Manager.memPool.getFromPool()
        if forBlock is None: forBlock = manager.Manager.chainMan.getHeight()
        # Check if this Is the bigBang block
        if manager.Manager.chainMan.getHeight() == 0: return declarations.chainConfig.blockMaxReward
        # Calculate mining reward
        blocksToMineMaxSupply = ((declarations.chainConfig.maxSupply * 2) / declarations.chainConfig.blockMaxReward)
        bigBangReward = (((blocksToMineMaxSupply - forBlock) / (blocksToMineMaxSupply)) * declarations.chainConfig.blockMaxReward) if not declarations.chainConfig.testNet else (blocksToMineMaxSupply * declarations.chainConfig.blockMaxReward)
        # Check if the mining reward exceeds the maximum of 20 or its equal or less than 0
        if bigBangReward > declarations.chainConfig.blockMaxReward: bigBangReward = declarations.chainConfig.blockMaxReward
        if bigBangReward < 0: bigBangReward = 0
        # Check if the max supply is exceeded or going to be exceeded
        if float(float(manager.Manager.wallet.getBalance(declarations.chainConfig.rewardName)) * -1) >= declarations.chainConfig.maxSupply: bigBangReward = 0
        if (generated := float(float(float(manager.Manager.wallet.getBalance(declarations.chainConfig.rewardName)) - bigBangReward) * -1)) >= declarations.chainConfig.maxSupply:
            if float(declarations.chainConfig.maxSupply) - float(generated) < 0: bigBangReward = 0
            else: bigBangReward = float(declarations.chainConfig.maxSupply) - float(generated)
        # Get the commission rewards
        commissionRewards = 0
        # For unconfirmed transaction was in the memPool get the commission and sum It to commissionRewards
        for trans in transactions:
            if not trans.get(mapping.Transactions.amount) <= 0:
                if not trans.get(mapping.Transactions.amount) == (trans.get(mapping.Transactions.realAmount) - (trans.get(mapping.Transactions.realAmount) / 100 * 0.01)):
                    # Remove the invalid transaction from the memPool
                    manager.Manager.memPool.removeFromPool(transactionToRemove=trans)
                else: commissionRewards += trans[mapping.Transactions.commission]  # Add commission to the commissionRewards
        # Calculate totalReward
        totalReward = float(bigBangReward + commissionRewards)
        return float(totalReward)

    @staticmethod
    def calculateDifficulty(lastHash, lastBlockAmount, blockReward):
        """
        Returns difficulty.
        """
        # If there aren't any block return the minDiff
        if manager.Manager.chainMan.getHeight() == 0: return int(declarations.miningConfig.minDiff)
        # Get last block hash
        lastBlockHash = str(lastHash)
        # Get the brute blocks first two numbers In hash
        difficultyFoundationNumber = ""
        # Loop for each character In the hash until we encounter with digit
        for character in lastBlockHash:
            if character.isdigit():
                # Get If the first number that Is going to be added Is not 0
                if character == "0":
                    if difficultyFoundationNumber == "": continue
                # Add the number to the difficultyFoundationNumber
                difficultyFoundationNumber += character
                # If they're already 2 numbers in difficultyFoundationNumber break
                if len(difficultyFoundationNumber) == 2: break
        # Get the difficulty based on the last block hash
        if difficultyFoundationNumber != "": hashBasedDiff = int(float(int(declarations.miningConfig.maxDiff) / 100) * int(difficultyFoundationNumber))
        else: hashBasedDiff = 0
        # Get the difficulty based on the amount of the transactions In the block
        amountBasedDiff = int(float(lastBlockAmount / blockReward) + declarations.miningConfig.minDiff)
        # Set final difficulty
        difficulty = int(amountBasedDiff if amountBasedDiff < declarations.miningConfig.maxDiff else (declarations.miningConfig.maxDiff - ((hashBasedDiff / 4) if hashBasedDiff != 0 or not hashBasedDiff < declarations.miningConfig.minDiff or not hashBasedDiff > declarations.miningConfig.maxDiff else float(0))))
        # Checks If the difficulty Is between the minimums and the maximums required
        if difficulty < declarations.miningConfig.minDiff:
            difficulty = declarations.miningConfig.minDiff
        elif difficulty > declarations.miningConfig.maxDiff:
            difficulty = declarations.miningConfig.maxDiff
        return int(difficulty)
