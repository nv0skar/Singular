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

from rich.console import Console, Style

class Exceptions:
    @staticmethod
    def handler(reason, hasToExit, show, type=""):
        """
        Handle tracebacks
        """
        # Print reason If show Is true
        if show:
            if type != "": Console().print("Error {}: {}".format(type, (reason if reason != "" else "Not specified")), style=Style(color="red", bold=True))
            else: Console().print("Error: {}".format((reason if reason != "" else "Not specified")), style=Style(color="red", bold=True))
        # Quit If exit Is true
        if hasToExit: exit()

    class Compromised(Exception):
        def __init__(self, reason="", hasToExit=False, show=True, type=""):
            Exceptions.handler(reason, hasToExit, show, type)
