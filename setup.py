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

from setuptools import find_packages, setup
import singular

setup(
    name="Singular",
    version=singular.globals.__version__,
    description="A unique blockchain made by humanity for humanity",
    python_requires=">=3.7.9",
    url=singular.globals.__url__,
    packages=find_packages(include=["singular"]),
    entry_points={
        'console_scripts': ['singular=singular:main.main'],
    },
)
