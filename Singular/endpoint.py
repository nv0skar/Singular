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

import threading
from . import declarations
from . import manager
from . import mapping
from . import block
from flask import Flask
from flask import request
from flask import jsonify
from werkzeug.exceptions import HTTPException
from waitress import serve

endpoint = Flask(str(declarations.core.agent))

class Endpoint:
    @staticmethod
    def init():
        """
        Initialize the server
        """
        if declarations.miningConfig.mining:
            declarations.status.walletServer = threading.Thread(target=Endpoint.serverStart)
            declarations.status.walletServer.start()
        else: Endpoint.serverStart()

    @staticmethod
    def serverStart():
        """
        Start the server
        """
        # Set the debug status
        endpoint.debug = bool(declarations.debugConfig.debug)
        # Disable the reloader
        endpoint.use_reloader = False
        # Start the server
        declarations.helpers.printer.sprint("main", "Initializing Web API on port {}".format(int(declarations.core.networking.defaultPort)))
        serve(endpoint, host="0.0.0.0", port=int(declarations.core.networking.defaultPort))

    class globals:
        @staticmethod
        @endpoint.route("/", methods=["GET"])
        async def info():
            """
            Return info about the node
            """
            declarations.helpers.printer.sprint("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")))
            return jsonify({"network": str(declarations.chainConfig.name), "networkMagicID": str(declarations.chainConfig.magicID), "protocolVersion": str(declarations.core.protocolVersion), "agent": str(declarations.core.agent)}), 200

        @staticmethod
        @endpoint.errorhandler(HTTPException)
        def handle_exception(error):
            """
            Return JSON instead of HTML for HTTP errors.
            """
            declarations.helpers.printer.sprint("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")))
            return jsonify({"code": error.code, "name": error.name, "description": error.description})

    class node:
        @staticmethod
        @endpoint.route("/node/get/block/<blockNumber>", methods=["GET"])
        async def getBlock(blockNumber):
            """
            Send the block
            """
            declarations.helpers.printer.sprint("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")))
            try: return jsonify({"blockNumber": str(blockNumber), "block": dict(manager.Manager.chainMan.getChain(blockNumber))}), 200
            except (declarations.helpers.baseExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400

        @staticmethod
        @endpoint.route("/node/get/memPool", methods=["GET"])
        async def getMemPool():
            """
            Send the memPool
            """
            declarations.helpers.printer.sprint("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")))
            try: return jsonify({"transactions": list(manager.Manager.memPool.getFromPool())}), 200
            except (declarations.helpers.baseExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400

        @staticmethod
        @endpoint.route("/node/add/block", methods=["POST"])
        async def addToChain():
            """
            Add block to the chain
            """
            declarations.helpers.printer.sprint("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")))
            try:
                blockToAdd = block.Block(list(request.json(mapping.Block.transactions)))
                blockToAdd.blockNumber = int(request.json(mapping.Block.blockNumber))
                blockToAdd.difficulty = float(request.json(mapping.Block.difficulty))
                blockToAdd.nonce = float(request.json(mapping.Block.nonce))
                blockToAdd.miner = str(request.json(mapping.Block.miner))
                blockToAdd.minerTime = float(request.json(mapping.Block.minerTime))
                blockToAdd.lastBlockHash = str(request.json(mapping.Block.lastBlockHash))
                blockToAdd.time = float(request.json(mapping.Block.time))
                blockToAdd.networkMagicID = str(request.json(mapping.Block.networkMagicID))
                blockToAdd.protocolVersion = str(request.json(mapping.Block.protocolVersion))
                blockManagerResponse = manager.Manager.chainMan.addToChain(blockToAdd.get(), True, True, clean=True)
            except (declarations.helpers.baseExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400
            if blockManagerResponse: return jsonify({"status": "success", "reason": "Apparently everything went fine ;)"}), 200
            else: return jsonify({"status": "failed", "reason": "Block integrity check failed"}), 400

        @staticmethod
        @endpoint.route("/node/add/memPool", methods=["POST"])
        async def addToMemPool():
            """
            Add transaction to the memPool
            """
            declarations.helpers.printer.sprint("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")))
            try: transactionManagerResponse = manager.Manager.wallet.transaction(request.json(mapping.Transactions.sender), request.json(mapping.Transactions.receiver), request.json(mapping.Transactions.realAmount), request.json(mapping.Transactions.signature), request.json(mapping.Transactions.time))
            except (declarations.helpers.baseExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400
            if transactionManagerResponse: return jsonify({"status": "success", "reason": "Apparently everything went fine ;)"}), 200
            else: return jsonify({"status": "failed", "reason": "Transaction confirmation failed"}), 400

    class wallet:
        @staticmethod
        @endpoint.route("/wallet/balance/<wallet>", methods=["GET"])
        async def getBalance(wallet):
            """
            Check the balance for a given wallet
            """
            declarations.helpers.printer.sprint("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")))
            return jsonify({"address": str(wallet), "balance": float(manager.Manager.wallet.getBalance(str(wallet)))}), 200

        @staticmethod
        @endpoint.route("/wallet/transactions/<wallet>", methods=["GET"])
        async def getTransactions(wallet):
            """
            Check the transactions of the given wallet
            """
            declarations.helpers.printer.sprint("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")))
            transactions = manager.Manager.wallet.getTransactions(str(wallet))
            return jsonify({"address": str(wallet), "transactions": list(transactions)}), 200

        @staticmethod
        @endpoint.route("/wallet/issue", methods=["POST"])
        async def makeTransaction():
            """
            Issue transaction
            """
            declarations.helpers.printer.sprint("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")))
            try: transactionManagerResponse = manager.Manager.wallet.transaction(request.json(mapping.Transactions.sender), request.json(mapping.Transactions.receiver), request.json(mapping.Transactions.realAmount), request.json(mapping.Transactions.signature), request.json(mapping.Transactions.time))
            except (declarations.helpers.baseExceptions): return jsonify({"status": "failed", "reason": "Invalid message format"}), 400
            if transactionManagerResponse: return jsonify({"status": "success", "reason": "Apparently everything went fine ;)"}), 200
            else: return jsonify({"status": "failed", "reason": "Transaction confirmation failed"}), 400
