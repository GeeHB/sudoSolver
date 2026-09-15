#!/usr/bin/env python
#
#
# coding=UTF-8
#
#   File        :   sudoSolver.py
#
#   Author      :   GeeHB
#
#   Description :   Display, edit and solve sudokus

#                   Command line version
#

import sys

import pygameSolver
from options import (
    PYTHON_VER_MAJ,
    PYTHON_VER_MIN,
    options,
)
from solver import solver

# Entry point
if "__main__" == __name__:
    # Check python ver.
    #
    ver = sys.version_info
    if (
        ver.major < PYTHON_VER_MAJ
        or ver.major == PYTHON_VER_MAJ
        and ver.minor < PYTHON_VER_MIN
    ):
        print(
            f"Invalid python version. Expected min. release {PYTHON_VER_MAJ}.{PYTHON_VER_MIN}"
        )
        sys.exit(2)

    # Parse command line
    #
    params = options()
    if not params.parse():
        sys.exit(1)

    print(params.version())

    try:
        mySolver : solver = pygameSolver.pygameSolver(params)

        mySolver.start()
        mySolver.initialize()
    except Exception as e:  # noqa: BLE001
        print(f"{type(e).__name__}: {e}")
        print("Unknown error")
    finally:
        mySolver.end()



# EOF
