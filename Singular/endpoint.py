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
        declarations.status.walletServer = threading.Thread(target=Endpoint.serverStart)
        declarations.status.walletServer.start()

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
            return jsonify({"network": str(declarations.chainConfig.name), "networkMagicNumber": str(declarations.chainConfig.magicNumber), "protocolVersion": str(declarations.core.protocolVersion), "agent": str(declarations.core.agent)}), 200

        @staticmethod
        @endpoint.errorhandler(HTTPException)
        def handle_exception(error):
            """
            Return JSON instead of HTML for HTTP errors.
            """
            return jsonify({"code": error.code, "name": error.name, "description": error.description})

    class node:
        @staticmethod
        @endpoint.route("/node/get/block/<blockNumber>", methods=["GET"])
        async def getBlock(blockNumber):
            """
            Send the block
            """
            try: return jsonify({"blockNumber": str(blockNumber), "block": dict(manager.Manager.chainMan.getChain(blockNumber))}), 200
            except (declarations.helpers.baseExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400

        @staticmethod
        @endpoint.route("/node/get/memPool", methods=["GET"])
        async def getMemPool():
            """
            Send the memPool
            """
            try: return jsonify({"transactions": list(manager.Manager.memPool.getFromPool())}), 200
            except (declarations.helpers.baseExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400

        @staticmethod
        @endpoint.route("/node/add/block", methods=["POST"])
        async def addToChain():
            """
            Add block to the chain
            """
            try:
                blockToAdd = block.Block(list(request.json("transactions")))
                blockToAdd.blockNumber = int(request.json("blockNumber"))
                blockToAdd.difficulty = float(request.json("difficulty"))
                blockToAdd.nonce = float(request.json("nonce"))
                blockToAdd.miner = str(request.json("miner"))
                blockToAdd.minerTime = float(request.json("minerTime"))
                blockToAdd.lastBlockHash = str(request.json("lastBlockHash"))
                blockToAdd.time = float(request.json("time"))
                blockToAdd.networkMagicNumber = str(request.json("networkMagicNumber"))
                blockToAdd.protocolVersion = str(request.json("protocolVersion"))
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
            try: transactionManagerResponse = manager.Manager.wallet.transaction(request.json("sender"), request.json("receiver"), request.json("realAmount"), request.json("signature"), request.json("time"))
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
            return jsonify({"address": str(wallet), "balance": float(manager.Manager.wallet.getBalance(str(wallet)))}), 200

        @staticmethod
        @endpoint.route("/wallet/transactions/<wallet>", methods=["GET"])
        async def getTransactions(wallet):
            """
            Check the transactions of the given wallet
            """
            transactions = manager.Manager.wallet.getTransactions(str(wallet))
            return jsonify({"address": str(wallet), "transactions": list(transactions)}), 200

        @staticmethod
        @endpoint.route("/wallet/issue", methods=["POST"])
        async def makeTransaction():
            """
            Issue transaction
            """
            try: transactionManagerResponse = manager.Manager.wallet.transaction(request.json("sender"), request.json("receiver"), request.json("realAmount"), request.json("signature"), request.json("time"))
            except (declarations.helpers.baseExceptions): return jsonify({"status": "failed", "reason": "Invalid message format"}), 400
            if transactionManagerResponse: return jsonify({"status": "success", "reason": "Apparently everything went fine ;)"}), 200
            else: return jsonify({"status": "failed", "reason": "Transaction confirmation failed"}), 400
