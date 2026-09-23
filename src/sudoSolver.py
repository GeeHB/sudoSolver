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

import solver
from options import (
    PYTHON_VER_MAJ,
    PYTHON_VER_MIN,
    options,
)
from pygameSolver import pygameSolverApp
from wxSolver import wxSolverApp

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

    mySolverApp : solver.solverApp = solver.solverApp(params)
    try:
        if params.wxGUI:
            mySolverApp = wxSolverApp(params)
        else:
            mySolverApp = pygameSolverApp(params)

        mySolverApp.initialize()
        mySolverApp.start()
    except Exception as e:  # noqa: BLE001
        print(f"{type(e).__name__}: {e}")
        print("Unknown error")
    finally:
        mySolverApp.end()

# EOF
