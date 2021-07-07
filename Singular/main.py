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

from . import manager
from . import frontend
from . import parser
from . import integrity
import rich.traceback

def main():
    """
    Parse arguments, show frontend and initialize
    """
    try:
        # Set the traceback parser
        rich.traceback.install()
        # Parse arguments
        passedArguments = parser.Arguments.parse()
        # Check integrity
        integrity.Integrity.check()
        # Show frontend
        frontend.Frontend.initial(passedArguments)
        # Initialize
        manager.Manager.protocol.loop(True, frontend.Frontend.show.blockMined)
    except KeyboardInterrupt:
        pass
