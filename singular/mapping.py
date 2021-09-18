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

class commons:
    dataPath = "dataPath"
    inform = "inform"
    minerAddress = "minerAddress"
    minerEndpoint = "minerEndpoint"
    mining = "mining"
    multiprocessingMining = "multiprocessingMining"
    timeToCheck = "timeToCheck"

class block:
    blockNumber = "blockNumber"
    lastBlockHash = "lastBlockHash"
    transactions = "transactions"
    difficulty = "difficulty"
    nonce = "nonce"
    minerAddress = "minerAddress"
    minerEndpoint = "minerEndpoint"
    time = "time"
    minerTime = "minerTime"
    hash = "hash"
    protocolVersion = "protocolVersion"
    netID = "netID"

class transactions:
    sender = "sender"
    receiver = "receiver"
    amount = "amount"
    realAmount = "realAmount"
    commission = "commission"
    time = "time"
    signature = "signature"

class network:
    name = "name"
    initAddress = "initAddress"
    initEndpoint = "initEndpoint"
    netID = "id"
    maxSupply = "maxSupply"
    maxAmount = "maxAmount"
    maxReward = "maxReward"
    rewardName = "rewardName"
    minDiff = "minDiff"
    maxDiff = "maxDiff"
    testNet = "testNet"

class nodes:
    address = "address"
    endpoint = "endpoint"

class networking:
    port = "port"
    class api:
        protocol = "http://"
        info = "/"
        class node:
            class get:
                block = "/node/get/block"
                memPool = "/node/get/memPool"
            class add:
                block = "/node/add/block"
                memPool = "/node/add/memPool"
        class wallet:
            class get:
                balance = "/wallet/balance"
                transactions = "/wallet/transactions"
            class add:
                issueTransaction = "/wallet/issue"
    