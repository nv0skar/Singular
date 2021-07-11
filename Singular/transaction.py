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

from time import time as getTime
from . import declarations
from . import manager
from . import formulae
from . import helper
import base64
import nacl.signing, nacl.exceptions
import binascii

class Transaction:
    def __init__(self, sender, receiver, realAmount, signature=None, time=getTime()):
        self.sender = sender
        self.receiver = receiver
        self.realAmount = float(realAmount)
        self.commission = float((self.realAmount/100) * 0.01)
        self.amount = float(self.realAmount - self.commission)
        self.time = time
        self.signature = signature

    def compose(self):
        '''
        Compose the transaction into a string with the transaction data in It.
        '''
        return str("({}-{}-{}-{})@{}".format(self.sender,self.receiver,float(self.realAmount),float(self.amount), self.time))

    def verify(self):
        """
        Verifies the identity of the transaction's issuer
        """
        try:
            # Verify If the a transaction with the same signature Is already In the chain
            try:
                if manager.Manager.chainMan.getHeight() != 0:
                    for blockMinedNumber in range(manager.Manager.chainMan.getHeight()):
                        blockMined = manager.Manager.chainMan.getChain(blockMinedNumber)
                        for trans in blockMined.get("transactions"):
                            if trans.get("signature") == self.signature:
                                helper.report("Transaction verifier", "Repeated signature in the chain")
                                return False
                else:
                    # Avoid making a transaction If there aren't any blocks
                    helper.report("Transaction verifier", "There isn't any block in the chain", level=declarations.helpers.messageLevelTypes.warning)
                    return False
            except AttributeError:
                helper.report("Transaction verifier", "Failed verification")
                pass
            # Decode the address and the signature from hexadecimal
            address = base64.b16decode(self.sender)
            signature = base64.b16decode(self.signature)
            # Get the verification key
            verification = nacl.signing.VerifyKey(bytes(address))
            # Checks the message
            try:
                verification.verify(str(self.compose()).encode(), signature)
                return True
            except (nacl.exceptions.BadSignatureError):
                helper.report("Transaction verifier", "Bad signature")
                return False
        except (binascii.Error) as e:
            helper.report("Transaction verifier", str(e))
            return False

    def check(self, fetched=False):
        """
        Checks If the transaction could be added to the memPool or should be rejected
        """
        # Get memPool
        memPool = manager.Manager.memPool.getFromPool()
        # Check If the sender Is the receiver or the sender or the receiver Is empty
        if str(self.sender) == "" or str(self.receiver) == "" or str(self.sender) == str(self.receiver): return False
        # Check If the sender Is the reward name
        if str(self.sender) == str(declarations.chainConfig.rewardName):
            # Check If there Is already a reward transaction in the memPool
            for trans in memPool:
                if str(trans.get("sender")) == str(declarations.chainConfig.rewardName) and not fetched:
                    helper.report("Transaction checker", "There Is already a reward transaction in the memPool")
                    return False
            return True
        # Checks the identity
        if not self.verify():
            # The identity Is not valid!
            helper.report("Transaction checker", "The identity is not valid")
            return False
        # Checks If the realAmount Is more than the maxAmount and If the realAmount or the amount Is 0 or less
        if self.realAmount > declarations.chainConfig.maxAmount or self.realAmount <= 0 or self.amount <= 0:
            helper.report("Transaction checker", "Size of transaction out of bounds")
            return False
        # Check If the object Is going to be used to check transactions
        if fetched is False:
            # Get memPool and check If the transaction Is duplicated
            for trans in memPool:
                if str(trans.get("sender")) == self.sender and str(trans.get("receiver")) == self.receiver:
                    helper.report("Transaction checker", "The sender and receiver are the same")
                    return False
            # Declare senders balance
            balance = manager.Manager.wallet.getBalance(self.sender)
            # Check if the sender has enough balance and returns It If there Isn't any block mined yet
            if (manager.Manager.chainMan.getChain()) is not None:
                if balance <= 0 or (balance - self.realAmount) < 0:
                    helper.report("Transaction checker", "The sender has not have enough balance")
                    return False
            else:
                # Avoid making a transaction If there Isn't any blocks
                helper.report("Transaction checker", "There isn't any block in the chain", level=declarations.helpers.messageLevelTypes.warning)
                return False
        # Check If the commission Is calculated correctly
        if not self.amount == (self.realAmount - (self.realAmount / 100 * 0.01)): return False
        # The transaction could be added to the memPool
        return True

    def get(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "realAmount": self.realAmount,
            "commission": self.commission,
            "time": self.time,
            "signature": self.signature,
        }

class utils:
    @staticmethod
    def rewardTransactionComposer(miner, reward) -> dict:
        """
        Compose reward transaction
        """
        return Transaction(declarations.chainConfig.rewardName, miner, reward, "Unnecessary!").get()

    @staticmethod
    def prepare(transactions, check=False):
        """
        Prepare transactions to be added to the chain
        """
        # Get all transactions of the memPool
        transactionsMemPool = list(transactions)
        # Check if the reward transaction of the last block is added if check is False
        if not check and (manager.Manager.chainMan.getHeight()) != 0:
            lastBlock = manager.Manager.chainMan.getChain()
            lastBlockInfo = dict(miner=lastBlock.get("miner"), reward=formulae.Formulae.calculateReward(lastBlock.get("transactions"), lastBlock.get("blockNumber")))
            rewardTransInMemPool = False
            for trans in transactionsMemPool:
                if str(trans.get("sender")) == str(lastBlockInfo.get("miner")): rewardTransInMemPool = True; break
            if not rewardTransInMemPool: transactionsMemPool.append(utils.rewardTransactionComposer(str(lastBlockInfo.get("miner")), str(lastBlockInfo.get("reward"))))
        # For each transaction make some checks
        for trans in list(transactionsMemPool):
            sender, receiver, amount, realAmount, commission, signature, time = trans.get("sender"), trans.get("receiver"), trans.get("amount"), trans.get("realAmount"), trans.get("commission"), trans.get("signature"), trans.get("time")
            # Make transaction object
            transToVerify = Transaction(sender, receiver, realAmount, signature, time)
            # Verify transaction
            if not transToVerify.check(True):
                # Remove transactions from junk
                transactionsMemPool.remove(trans)
        return list(transactionsMemPool)
