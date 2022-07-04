# Singular
# Copyright (C) 2022 Oscar
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
import multiprocessing
import signal
from . import declarations
from . import manager
from . import frontend
from . import parser
from . import integrity
import rich.traceback

def kill(*args):
    """
    Terminate process
    """
    # Terminate all the subprocesses
    for process in multiprocessing.active_children():
        try: process.kill()
        except: os.kill(process.pid, signal.SIGKILL)
    try: exit()
    except: os.kill(os.getpid(), signal.SIGKILL)

def main():
    """
    Parse arguments, show frontend and initialize
    """
    try:
        # Catch SIGINT signal
        signal.signal(signal.SIGINT, kill)
        # Set the traceback parser
        rich.traceback.install()
        # Parse arguments
        args = parser.argParser.parse()
        # Check integrity
        integrity.integrity.check()
        # Show frontend
        frontend.frontend.initial()
        # Initialize
        manager.manager.main.loop(True)
    except KeyboardInterrupt:
        pass
