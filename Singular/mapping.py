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

class Commons:
    dataPath = "dataPath"
    minerAddress = "minerAddress"
    mining = "mining"
    multiprocessingMining = "multiprocessingMining"

class Block:
    blockNumber = "blockNumber"
    lastBlockHash = "lastBlockHash"
    transactions = "transactions"
    difficulty = "difficulty"
    nonce = "nonce"
    miner = "miner"
    time = "time"
    minerTime = "minerTime"
    hash = "hash"
    protocolVersion = "protocolVersion"
    networkMagicID = "networkMagicID"

class Transactions:
    sender = "sender"
    receiver = "receiver"
    amount = "amount"
    realAmount = "realAmount"
    commission = "commission"
    time = "time"
    signature = "signature"

class Network:
    name = "name"
    bootstrapIP = "bootstrapIP"
    magicID = "magicID"
    maxSupply = "maxSupply"
    blockMaxReward = "blockMaxReward"
    rewardName = "rewardName"
    maxAmount = "maxAmount"
    minDiff = "minDiff"
    maxDiff = "maxDiff"
    testNet = "testNet"

class Networking:
    port = "port"
    