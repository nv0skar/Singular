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
from flask import Flask
from flask import request
from flask import jsonify
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
        serve(endpoint, host="0.0.0.0", port=int(declarations.core.networking.defaultPort))

    class wallet:
        @staticmethod
        @endpoint.route("/", methods=["GET"])
        async def info():
            """
            Return info about the node
            """
            return jsonify({"network": str(declarations.chainConfig.name), "networkMagicNumber": str(declarations.chainConfig.magicNumber), "protocolVersion": str(declarations.core.protocolVersion), "agent": str(declarations.core.agent)}), 200

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
            except (AttributeError, TypeError, ValueError): return jsonify({"status": "failed", "reason": "Invalid message format"}), 400
            if transactionManagerResponse: return jsonify({"status": "success"}), 200
            else: return jsonify({"status": "failed", "reason": "Transaction confirmation failed"}), 400
