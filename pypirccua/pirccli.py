#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2024, Ondrej Vanka
# 
# File:         pirccli.py
# Description:  PiRc - cli
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

from .pidbcard import PiDbCard
import statistics

def pirc_generate_stats(file_path):
    """Generate and display statistics for the file."""
    parser = PiDbCard(file_path)
    data = parser.parse_file()

    print(f"Statistics for {file_path}:")
    print("-" * 40)

    # Logical subunit statistics
    print("Logical Layers:")
    for subunit in data.get("subunits", []):
        relay_counts = list(subunit["relays"].values())
        max_count = max(relay_counts, default=0)
        mean_count = round(sum(relay_counts) / len(relay_counts), 2) if relay_counts else 0
        std_dev = round(statistics.stdev(relay_counts), 2) if len(relay_counts) > 1 else 0
        print(f"  Subunit {subunit['layer_id']}:")
        print(f"    Max Relay Count: {max_count}")
        print(f"    Mean Operations: {mean_count}")
        print(f"    Standard Deviation: {std_dev}")

    # Physical layer statistics
    print("\nPhysical Layers:")
    for loop in data.get("physical_layers", []):
        relay_counts = list(loop["relays"].values())
        max_count = max(relay_counts, default=0)
        mean_count = round(sum(relay_counts) / len(relay_counts), 2) if relay_counts else 0
        std_dev = round(statistics.stdev(relay_counts), 2) if len(relay_counts) > 1 else 0
        print(f"  Loop {loop['loop_id']}:")
        print(f"    Max Relay Count: {max_count}")
        print(f"    Mean Operations: {mean_count}")
        print(f"    Standard Deviation: {std_dev}")


def pirc_export_stats(file_path, output_file):
    """Export statistics to a file."""
    parser = PiDbCard(file_path)
    data = parser.parse_file()

    with open(output_file, "w") as file:
        file.write(f"Statistics for {file_path}:\n")
        file.write("-" * 40 + "\n")

        # Logical subunit statistics
        file.write("Logical Layers:\n")
        for subunit in data.get("subunits", []):
            relay_counts = list(subunit["relays"].values())
            max_count = max(relay_counts, default=0)
            mean_count = round(sum(relay_counts) / len(relay_counts), 2) if relay_counts else 0
            std_dev = round(statistics.stdev(relay_counts), 2) if len(relay_counts) > 1 else 0
            file.write(f"  Subunit {subunit['layer_id']}:\n")
            file.write(f"    Max Relay Count: {max_count}\n")
            file.write(f"    Mean Operations: {mean_count}\n")
            file.write(f"    Standard Deviation: {std_dev}\n")

        # Physical layer statistics
        file.write("\nPhysical Layers:\n")
        for loop in data.get("physical_layers", []):
            relay_counts = list(loop["relays"].values())
            max_count = max(relay_counts, default=0)
            mean_count = round(sum(relay_counts) / len(relay_counts), 2) if relay_counts else 0
            std_dev = round(statistics.stdev(relay_counts), 2) if len(relay_counts) > 1 else 0
            file.write(f"  Loop {loop['loop_id']}:\n")
            file.write(f"    Max Relay Count: {max_count}\n")
            file.write(f"    Mean Operations: {mean_count}\n")
            file.write(f"    Standard Deviation: {std_dev}\n")

    print(f"Statistics exported to {output_file}")