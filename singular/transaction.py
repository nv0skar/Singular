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

import time as getTime
from . import declarations
from . import manager
from . import mapping
from . import formulae
from . import helper
import base64
import nacl.signing, nacl.exceptions
import binascii

class transaction:
    def __init__(self, sender, receiver, realAmount, signature=None, time=getTime.time()):
        self.sender = sender
        self.receiver = receiver
        self.realAmount = float(realAmount)
        self.commission = float((self.realAmount/100) * 0.01)
        self.amount = float(self.realAmount - self.commission)
        self.time = time
        self.signature = signature

    def compose(self):
        """
        Compose the transaction into a string with the transaction data in It.
        """
        return str("({}-{}-{}-{})@{}".format(self.sender,self.receiver,float(self.realAmount),float(self.amount), self.time))

    def verify(self):
        """
        Verifies the identity of the transaction's issuer
        """
        try:
            # Verify If the a transaction with the same signature Is already In the chain
            try:
                if manager.manager.chainMan.getHeight() != 0:
                    for blockMinedNumber in range(manager.manager.chainMan.getHeight()):
                        blockMined = manager.manager.chainMan.getChain(blockMinedNumber)
                        for trans in blockMined.get(mapping.block.transactions):
                            if trans.get(mapping.transactions.signature) == self.signature:
                                helper.reporter.report("transaction verifier", "Repeated signature in the chain")
                                return False
                else:
                    # Avoid making a transaction If there aren't any blocks
                    helper.reporter.report("transaction verifier", "There isn't any block in the chain", level=declarations.helpers.messageLevelTypes.warning)
                    return False
            except AttributeError:
                helper.reporter.report("transaction verifier", "Failed verification")
                pass
            # Decode the address and the signature from hexadecimal
            address = base64.b16decode(self.sender)
            signature = base64.b16decode(self.signature)
            # Get the verification key
            try:
                verification = nacl.signing.VerifyKey(bytes(address))
            except (ValueError) as e:
                helper.reporter.report("transaction verifier", str(e))
                return False
            # Checks the message
            try:
                verification.verify(str(self.compose()).encode(), signature)
                return True
            except (nacl.exceptions.BadSignatureError):
                helper.reporter.report("transaction verifier", "Bad signature")
                return False
        except (binascii.Error) as e:
            helper.reporter.report("transaction verifier", str(e))
            return False

    def check(self, fetched=False):
        """
        Checks If the transaction could be added to the memPool or should be rejected
        """
        # Get memPool
        memPool = manager.manager.memPool.getFromPool()
        # Check If the sender Is the receiver or the sender or the receiver Is empty
        if str(self.sender) == "" or str(self.receiver) == "" or str(self.sender) == str(self.receiver): return False
        # Check If the sender Is the reward name
        if str(self.sender) == str(declarations.chainConfig.rewardName):
            # Check If there Is already a reward transaction in the memPool
            for trans in memPool:
                if str(trans.get(mapping.transactions.sender)) == str(declarations.chainConfig.rewardName) and not fetched:
                    helper.reporter.report("transaction checker", "There Is already a reward transaction in the memPool")
                    return False
            return True
        # Checks the identity
        if not self.verify():
            # The identity Is not valid!
            helper.reporter.report("transaction checker", "The identity is not valid")
            return False
        # Checks If the realAmount Is more than the maxAmount and If the realAmount or the amount Is 0 or less
        if self.realAmount > declarations.chainConfig.maxAmount or self.realAmount <= 0 or self.amount <= 0:
            helper.reporter.report("transaction checker", "Size of transaction out of bounds")
            return False
        # Check If the object Is going to be used to check transactions
        if fetched is False:
            # Get memPool and check If the transaction Is duplicated
            for trans in memPool:
                if str(trans.get(mapping.transactions.sender)) == self.sender and str(trans.get(mapping.transactions.receiver)) == self.receiver:
                    helper.reporter.report("transaction checker", "The sender and receiver are the same")
                    return False
            # Declare senders balance
            balance = manager.manager.wallet.getBalance(self.sender)
            # Check if the sender has enough balance and returns It If there Isn't any block mined yet
            if (manager.manager.chainMan.getChain()) is not None:
                if balance <= 0 or (balance - self.realAmount) < 0:
                    helper.reporter.report("transaction checker", "The sender has not have enough balance")
                    return False
            else:
                # Avoid making a transaction If there Isn't any blocks
                helper.reporter.report("transaction checker", "There isn't any block in the chain", level=declarations.helpers.messageLevelTypes.warning)
                return False
        # Check If the commission Is calculated correctly
        if not self.amount == (self.realAmount - (self.realAmount / 100 * 0.01)): return False
        # The transaction could be added to the memPool
        return True

    def get(self):
        return {
            mapping.transactions.sender: self.sender,
            mapping.transactions.receiver: self.receiver,
            mapping.transactions.amount: self.amount,
            mapping.transactions.realAmount: self.realAmount,
            mapping.transactions.commission: self.commission,
            mapping.transactions.time: self.time,
            mapping.transactions.signature: self.signature,
        }

class utils:
    @staticmethod
    def rewardTransactionComposer(minerAddress, reward) -> dict:
        """
        Compose reward transaction
        """
        return transaction(declarations.chainConfig.rewardName, minerAddress, reward, "Unnecessary!", getTime.time()).get()

    @staticmethod
    def prepare(transactions, check=True):
        """
        Prepare transactions to be added to the chain
        """
        # Get all transactions of the memPool
        transactionsMemPool = list(transactions)
        # Check if the reward transaction of the last block is added if check is true
        if check and ((manager.manager.chainMan.getHeight()) != 0):
            lastBlock = manager.manager.chainMan.getChain()
            lastBlockInfo = dict(minerAddress=lastBlock.get(mapping.block.minerAddress), reward=formulae.formulae.calculateReward(lastBlock.get(mapping.block.transactions), lastBlock.get(mapping.block.blockNumber)))
            rewardTransInMemPool = False
            for trans in transactionsMemPool:
                if str(trans.get(mapping.transactions.receiver)) == str(lastBlockInfo.get("minerAddress")): rewardTransInMemPool = True; break
            if not rewardTransInMemPool: transactionsMemPool.append(utils.rewardTransactionComposer(str(lastBlockInfo.get("minerAddress")), str(lastBlockInfo.get("reward"))))
        # For each transaction make some checks
        for trans in list(transactionsMemPool):
            sender, receiver, amount, realAmount, commission, signature, time = trans.get(mapping.transactions.sender), trans.get(mapping.transactions.receiver), trans.get(mapping.transactions.amount), trans.get(mapping.transactions.realAmount), trans.get(mapping.transactions.commission), trans.get(mapping.transactions.signature), trans.get(mapping.transactions.time)
            # Make transaction object
            transToVerify = transaction(sender, receiver, realAmount, signature, time)
            # Verify transaction
            if not transToVerify.check(True):
                # Remove transactions from junk
                transactionsMemPool.remove(trans)
        return list(transactionsMemPool)
