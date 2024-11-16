#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2024, Ondrej Vanka
# 
# File:         __main__.py
# Description:  Qt PiRc Viewer - main app
# Version:      1.00
# Author:       Ondrej Vanka @aknavj <ondrej@vanka.net>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import argparse

from PyQt5.QtWidgets import QApplication
from .pircviewer import PircViewer
from .pirccli import *

def main():
    """Main entry point for the pypirccua application."""
    
    parser = argparse.ArgumentParser(description="pypirccua utility")
    subparsers = parser.add_subparsers(dest="command")
    
    # stats cmd
    stats_parser = subparsers.add_parser("stats", help="Generate and display statistics for a file")
    stats_parser.add_argument("file", help="Path to the DB file")

    # export stats command
    export_parser = subparsers.add_parser("export-stats", help="Export statistics to a file")
    export_parser.add_argument("file", help="Path to the DB file")
    export_parser.add_argument("output", help="Path to save the exported statistics")

	# args
    args = parser.parse_args()
    if args.command == "help":
        parser.print_help()
    elif args.command == "stats":
        pirc_generate_stats(args.file)
    elif args.command == "export-stats":
        pirc_export_stats(args.file, args.output)
    else:
        app = QApplication(sys.argv)
        viewer = PircViewer()
        viewer.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()