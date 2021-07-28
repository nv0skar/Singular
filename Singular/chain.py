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

import time
from . import manager
from . import miner
from . import block as bl
from . import formulae

class Chain:
    @staticmethod
    def mine(bruteBlock, autoCleanMemPool=True):
        """
        Mine to verify pending transactions
        """
        # Prepare the block for mining
        blockToMine = bl.utils.prepare(bruteBlock)
        # Copy blocks difficulty
        difficulty = blockToMine.difficulty
        # Defines the prefix of the hash according to the difficulty
        prefix = "0" * difficulty
        # Counts how much time takes to calculate the nonce
        initializingTime = float(time.time())
        # Initialize miner
        blockMined = miner.Miner.start(blockToMine, difficulty, prefix, initializingTime)
        # Check If the block was mined
        if blockMined is not None:
            # The nonce was found
            # Check If the block Is already In the chain
            try:
                if blockMined.get("blockNumber") == int(manager.Manager.chainMan.getChain().get("blockNumber")): return False, 0 # The block Is already In the chain!
            except (AttributeError, TypeError): pass
            # Now reward the miner!
            reward = formulae.Formulae.calculateReward()
            # Clean memPool If requested
            if autoCleanMemPool:
                manager.Manager.memPool.removeFromPool(clean=True)
            return blockMined, reward
        else: return False, 0
