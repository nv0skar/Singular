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
import random
from . import declarations
import multiprocessing

class Miner:
    class status:
        def __init__(self):
            self.newBlockMined = False

    @staticmethod
    def start(block, difficulty, prefix, initializingTime):
        """
        Starts the miner
        """
        declarations.status.mine.newBlockMined = False
        if declarations.miningConfig.multiprocessingMining:
            # Define a process shared object to retrieve the block mined
            blockToMine = multiprocessing.Queue()
            # Make event to stop processes when one finishes
            found = multiprocessing.Event()
            # Define processes pool
            pools = []
            # Append processes
            for _ in range(multiprocessing.cpu_count()):
                pools.append(multiprocessing.Process(target=Miner.mine, args=(block, difficulty, prefix, initializingTime, blockToMine, found)))
            # Start processes
            for process in pools:
                # Set daemon as True to avoid the KeyboardInterrupt exception to not be handled
                process.daemon = True
                # Start process
                process.start()
            # Wait until one process finishes
            while not found.is_set():
                # Check if there is a new block in the chain
                if declarations.status.mine.newBlockMined: return False
            # Wait for them to finish
            for process in pools: process.join()
            # Kill processes
            for process in pools: process.kill()
            # Get block
            blockMined = blockToMine.get()
        else:
            blockMined = Miner.mine(block, difficulty, prefix, initializingTime, None, None)
        # Return block mined
        if type(blockMined) is bool:
            return False
        else:
            return dict(blockMined)

    @staticmethod
    def mine(blockToMine, difficulty, prefix, initializingTime, passBlock, event):
        while Miner.utils.checkMultiprocessing(event):
            # Stage 5 - Set the miner time
            '''
            The miner time randomizes the hash, requiring more or less nonces.
            This makes the network less dependant of powerful computers.
            '''
            blockToMine.minerTime = float(time.time()) - initializingTime
            # Stage 6 - Set the nonce
            '''
            The following line calculate a random nonce to use each time
            '''
            blockToMine.nonce = random.randint(0, pow(10,77))
            # Check If the block Is mined
            if blockToMine.hashBlock()[:difficulty] == prefix:
                # The nonce was found
                if declarations.miningConfig.multiprocessingMining:
                    # Pass the block
                    passBlock.put(blockToMine.get())
                    # Set that one block was mined
                    event.set()
                return blockToMine.get()
        # If not more tries return
        return

    class utils:
        @staticmethod
        def checkMultiprocessing(event):
            """
            Check if multiprocessing is enabled
            """
            if event is None and not declarations.miningConfig.multiprocessingMining: return True
            if event is not None and declarations.miningConfig.multiprocessingMining: return (not event.is_set())
