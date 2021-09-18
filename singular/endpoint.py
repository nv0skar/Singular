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
# from . import startpoint
from . import helper
import json
from flask import Flask
from flask import request
from flask import jsonify
from waitress import serve
from werkzeug.exceptions import HTTPException

endpointMan = Flask(str(declarations.core.agent))

class endpoint:
    @staticmethod
    def init():
        """
        Initialize the server
        """
        if declarations.miningConfig.mining:
            endpointThread = threading.Thread(target=endpoint.serverStart)
            endpointThread.start()
        else: endpoint.serverStart()

    @staticmethod
    def serverStart():
        """
        Start the server
        """
        # Set the debug status
        endpointMan.debug = bool(helper.debugging.status())
        # Disable the reloader
        endpointMan.use_reloader = False
        # Start the server
        _, endpointPort = helper.networking.segmentEndpointAddress(str(declarations.config.minerEndpoint))
        helper.reporter.report("main", "Initializing Web API on port {}".format(int(endpointPort)))
        try: serve(endpointMan, host=str("0.0.0.0"), port=int(endpointPort))
        except (PermissionError) as e: helper.reporter.compromised("An error occurred while trying to initialize the Web API (Permission denied)".format(e), True)

    class globals:
        @staticmethod
        @endpointMan.route(mapping.networking.api.info, methods=["GET"])
        async def info():
            """
            Return info about the node
            """
            helper.reporter.report("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")), force=True)
            try: return jsonify({"network": str(declarations.chainConfig.name), "netID": str(declarations.chainConfig.netID), "protocolVersion": str(declarations.core.protocolVersion), "agent": str(declarations.core.agent)}), 200
            except (declarations.helpers.networkingExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400

        @staticmethod
        @endpointMan.errorhandler(HTTPException)
        def handle_exception(error):
            """
            Return JSON instead of HTML for HTTP errors.
            """
            helper.reporter.report("networking", "Request on {} from {}; User-Agent: {}; Returning error message".format(request.url, request.remote_addr, request.headers.get("User-Agent")), level=declarations.helpers.messageLevelTypes.warning)
            try: return jsonify({"status": "failed", "description": str(error.description)}), 404
            except (declarations.helpers.networkingExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400

    class node:
        class get:
            @staticmethod
            @endpointMan.route("{}/<blockNumber>".format(mapping.networking.api.node.get.block), methods=["GET"])
            async def g_Block(blockNumber):
                """
                Send the block
                """
                helper.reporter.report("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")), force=True)
                try:
                    if (helper.conversions.isInt(blockNumber)) and (int(blockNumber) > int(manager.manager.chainMan.getHeight())): return jsonify({"status": "failed", "reason": "The requested block it's not in the node's chain"}), 400
                    else: return jsonify(dict(manager.manager.chainMan.getChain((None) if (str(blockNumber) == "latest") else (int(blockNumber))))), 200
                except (declarations.helpers.networkingExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400

            @staticmethod
            @endpointMan.route(mapping.networking.api.node.get.memPool, methods=["GET"])
            async def g_MemPool():
                """
                Send the memPool
                """
                helper.reporter.report("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")), force=True)
                try: return jsonify({"transactions": list(manager.manager.memPool.getFromPool())}), 200
                except (declarations.helpers.networkingExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400

        class add:
            @staticmethod
            @endpointMan.route(mapping.networking.api.node.add.block, methods=["POST"])
            async def a_Block():
                """
                Add block to the chain
                """
                helper.reporter.report("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")), force=True)
                try:
                    # if startpoint.startpoint.sync(dict(request.json)): return jsonify({"status": "success", "reason": "Apparently everything went fine ;)"}), 200
                    # else: return jsonify({"status": "failed", "reason": "There was some error while trying to add the block to the chain"}), 400
                    if manager.manager.chainMan.addToChain(dict(request.json), True, True): return jsonify({"status": "success", "reason": "Apparently everything went fine ;)"}), 200
                    else: return jsonify({"status": "failed", "reason": "There was some error while trying to add the block to the chain"}), 400
                except (declarations.helpers.networkingExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400

            @staticmethod
            @endpointMan.route(mapping.networking.api.node.add.memPool, methods=["POST"])
            async def a_MemPool():
                """
                Add transaction to the memPool
                """
                helper.reporter.report("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")), force=True)
                try: transactionManagerResponse = manager.manager.wallet.transaction(request.json[mapping.transactions.sender], request.json[mapping.transactions.receiver], request.json[mapping.transactions.realAmount], request.json[mapping.transactions.signature], request.json[mapping.transactions.time])
                except (declarations.helpers.networkingExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400
                if transactionManagerResponse: return jsonify({"status": "success", "reason": "Apparently everything went fine ;)"}), 200
                else: return jsonify({"status": "failed", "reason": "Transaction confirmation failed"}), 400

    class wallet:
        class get:
            @staticmethod
            @endpointMan.route("{}/<wallet>".format(mapping.networking.api.wallet.get.balance), methods=["GET"])
            async def g_Balance(wallet):
                """
                Check the balance for a given wallet
                """
                helper.reporter.report("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")), force=True)
                try: return jsonify({"address": str(wallet), "balance": float(
                    manager.manager.wallet.getBalance(str(wallet)))}), 200
                except (declarations.helpers.networkingExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400

            @staticmethod
            @endpointMan.route("{}/<wallet>".format(mapping.networking.api.wallet.get.transactions), methods=["GET"])
            async def g_Transactions(wallet):
                """
                Check the transactions of the given wallet
                """
                helper.reporter.report("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")), force=True)
                try: transactions = manager.manager.wallet.getTransactions(str(wallet))
                except (declarations.helpers.networkingExceptions): return jsonify({"status": "failed", "reason": "There was some error while trying to process the request"}), 400
                return jsonify({"address": str(wallet), "transactions": list(transactions)}), 200

        class add:
            @staticmethod
            @endpointMan.route(mapping.networking.api.wallet.add.issueTransaction, methods=["POST"])
            async def issueTransaction():
                """
                Issue transaction
                """
                helper.reporter.report("networking", "Request on {} from {}; User-Agent: {}".format(request.url, request.remote_addr, request.headers.get("User-Agent")), force=True)
                try: transactionManagerResponse = manager.manager.wallet.transaction(request.json(mapping.transactions.sender), request.json(mapping.transactions.receiver), request.json(mapping.transactions.realAmount), request.json(mapping.transactions.signature), request.json(mapping.transactions.time))
                except (declarations.helpers.networkingExceptions): return jsonify({"status": "failed", "reason": "Invalid message format"}), 400
                if transactionManagerResponse: return jsonify({"status": "success", "reason": "Apparently everything went fine ;)"}), 200
                else: return jsonify({"status": "failed", "reason": "Transaction confirmation failed"}), 400
