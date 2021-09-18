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

import os
import signal
from . import declarations
import nacl.signing, nacl.exceptions
import superPrinter
from rich.console import Console, Style

class reporter:
    @staticmethod
    def report(caller, message, level=superPrinter.levels.info, force=False):
        """
        Print messages
        """
        if (level == superPrinter.levels.info) and (bool(debugging.status()) or bool(force) or bool(declarations.status.inform)): declarations.helpers.printer.sprint(caller, message, level=level); return
        elif (level != superPrinter.levels.info): declarations.helpers.printer.sprint(caller, message, level=level); return

    @staticmethod
    def compromised(reason="", end=False):
        Console().print("Error: {}".format(reason if reason != "" else "Not specified"), style=Style(color="red", bold=True))
        # Kill process if end is set
        if end: os.kill(os.getpid(), signal.SIGKILL)

class debugging:
    @staticmethod
    def status() -> bool:
        """
        Return debugging status
        """
        return bool(declarations.status.debug)

    @staticmethod
    def enableDebug():
        """
        Enables debug mode
        """
        # Set the debug var to true
        declarations.status.debug = True
        # Enable debugging behaviours
        declarations.miningConfig.maxDiff = 1
        declarations.miningConfig.minDiff = 1

class networking:
    @staticmethod
    def segmentEndpointAddress(endpoint) -> (str, int):
        """
        Separate the ip address and port from string
        """
        times = 0
        for charNum in range(0, len(endpoint)):
            currentChar = endpoint[(len(endpoint)-charNum)-1]
            if currentChar != ":": times += 1
            else: return (endpoint[:((len(endpoint)-1)-times)], endpoint[((len(endpoint))-times):])

class address:
    @staticmethod
    def generate():
        """
        Generate a new address
        """
        privateKey = nacl.signing.SigningKey.generate()
        publicKey = privateKey.verify_key
        return (publicKey, privateKey)

class conversions:
    @staticmethod
    def isInt(value) -> bool:
        """
        Check if the passed value is an integer
        """
        try: int(value); return True
        except (ValueError): return False
