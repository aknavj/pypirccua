#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2024, Ondrej Vanka
# 
# File:         pitableview.py
# Description:  Qt Pi Database File parsed into Data Table View
# Version:      1.01
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

from pidbcard import *
from heatmaprange import *

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QTabWidget, QSplitter
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import statistics
import re

class PiTableView(QTabWidget):

    cell_selected = pyqtSignal(str)  # signal to emit the relay line text
    statistics_row_selected = pyqtSignal(str)  # signal to emit when a statistics row is selected

    def __init__(self, heatmap_range_widget, parent=None):
        super().__init__(parent)
        self.layer_id = None  # logical or physical layer id
        self.is_logical = True  # flag for logical or physical
        
        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.stats_table = QTableWidget()

        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)
        self.parsed_data = None
        self.line_mapping = {}
        self.heatmap_range_widget = heatmap_range_widget  # ref to HeatMapRange widget
        self.tables = [] # store references to all QTableWidgets (stupid HeatMapRange hotreload :D)

    def set_layer(self, layer_id, is_logical=True):
        self.layer_id = layer_id
        self.is_logical = is_logical

    def mousePressEvent(self, event):
        """Handle mouse press events and highlight table items."""
        # get the current table in the active tab
        current_widget = self.currentWidget()
        if isinstance(current_widget, QTableWidget):
            # get the item at the mouse click position
            table_item = current_widget.itemAt(event.pos())
            if table_item:
                table_item.setSelected(True)

    #def mousePressEvent(self, event):
    #    """Emit the relay line for the selected cell."""
    #    super().mousePressEvent(event)
    #    item = self.itemAt(event.pos())
    #    if item and self.layer_id is not None:
    #        row, col = item.row(), item.column()
    #        bit_number = row * self.columnCount() + col + 1
    #        if self.is_logical:
    #            relay_line = f"R;L;S{self.layer_id}BIT{bit_number};{item.text()}"
    #        else:
    #            relay_line = f"R;P;L{self.layer_id}BIT{bit_number};{item.text()}"
    #        self.cell_selected.emit(relay_line)

    def populate_tabs(self):
        """Populate tabs with parsed data."""
        self.clear_tabs()

        if not self.parsed_data:
            return
        
        # stats
        stats_widget = self.create_statistics_tab()
        self.tab_widget.addTab(stats_widget, "Statistics")

        # logical subunits
        for subunit in self.parsed_data.get("subunits", []):
            subunit_widget = self.create_subunit_tab(subunit)
            self.tab_widget.addTab(subunit_widget, f"Subunit {subunit['layer_id']} - {subunit['description']}")

        # physical loops
        for loop in self.parsed_data.get("physical_layers", []):
            loop_widget = self.create_physical_tab(loop)
            self.tab_widget.addTab(loop_widget, f"Loop {loop['loop_id']} - physical")

    def clear_tabs(self):
        """Clear tabs."""
        self.stats_table.clear()
        self.tables.clear()
        self.tab_widget.clear()

    def create_subunit_tab(self, subunit):
        """Create a tab for a logical subunit."""
        widget = QWidget()
        layout = QVBoxLayout()

        rows, cols = subunit["rows"], subunit["cols"]
        table = QTableWidget(rows, cols)

        if cols > 1:  # matrix view
            table.setHorizontalHeaderLabels([f"Col {c + 1}" for c in range(cols)])
            table.setVerticalHeaderLabels([f"Row {r + 1}" for r in range(rows)])
        else:  # column view
            table.setHorizontalHeaderLabels(["Counts"])
            table.setVerticalHeaderLabels([f"RL{r + 1}" for r in range(rows)])

        # heatmap ranges
        ranges = self.heatmap_range_widget.get_ranges()

        for (row, col), value in subunit["relays"].items():
            item = QTableWidgetItem(str(value))
            item.setBackground(get_heatmap_color(value, ranges))
            table.setItem(row, col, item)

        self.tables.append(table)  # add table reference to the list

        layout.addWidget(table)

        # add statistics graph
        graph = self.create_statistics_graph(subunit["relays"])
        layout.addWidget(graph)

        widget.setLayout(layout)
        return widget

    def create_physical_tab(self, loop):
        """Create a tab for a physical loop."""
        widget = QWidget()
        layout = QVBoxLayout()

        rows, cols = loop["rows"], loop["cols"]
        table = QTableWidget(rows, cols)

        if cols > 1:  # matrix view
            table.setHorizontalHeaderLabels([f"Col {c + 1}" for c in range(cols)])
            table.setVerticalHeaderLabels([f"Row {r + 1}" for r in range(rows)])
        else:  # column view
            table.setHorizontalHeaderLabels(["Counts"])
            table.setVerticalHeaderLabels([f"RL{r + 1}" for r in range(rows)])

        # heatmap ranges
        ranges = self.heatmap_range_widget.get_ranges()

        for (row, col), value in loop["relays"].items():
            item = QTableWidgetItem(str(value))
            item.setBackground(get_heatmap_color(value, ranges))
            table.setItem(row, col, item)

        self.tables.append(table)  # add table reference to the list

        layout.addWidget(table)

        # statistics graph
        graph = self.create_statistics_graph(loop["relays"])
        layout.addWidget(graph)

        widget.setLayout(layout)
        return widget
    
    def create_statistics_graph(self, relays):
        """Create a statistics graph for relay data."""
        # extract values
        counts = [value for value in relays.values()]

        # create a matplotlib
        fig = Figure(figsize=(5, 3))
        ax = fig.add_subplot(111)

        # plot a histogram of counts
        ax.hist(counts, bins=20, color='blue', edgecolor='black')
        ax.set_title("Relay Count Distribution")
        ax.set_xlabel("Relay Count")
        ax.set_ylabel("Frequency")

        # add the mean line
        mean_value = sum(counts) / len(counts) if counts else 0
        ax.axvline(mean_value, color='red', linestyle='dashed', label=f"Mean: {mean_value:.2f}")
        ax.legend()

        # wrap figure in a FigureCanvas
        canvas = FigureCanvas(fig)
        return canvas
    
    def create_statistics_for_layer(self, relays):
        """Generate a statistics table for a single layer."""
        widget = QTableWidget(4, 2)
        widget.setHorizontalHeaderLabels(["Metric", "Value"])
        widget.setVerticalHeaderLabels([
            "Max Relay Count",
            "Mean Operations",
            "Total Operations",
            "Standard Deviation"
        ])

        # calculate statistics
        values = list(relays.values())
        widget.setItem(0, 1, QTableWidgetItem(str(max(values, default=0))))
        widget.setItem(1, 1, QTableWidgetItem(f"{np.mean(values):.2f}" if values else "0.00"))
        widget.setItem(2, 1, QTableWidgetItem(str(sum(values, 0))))
        widget.setItem(3, 1, QTableWidgetItem(f"{np.std(values):.2f}" if len(values) > 1 else "0.00"))

        return widget

    def create_statistics_tab(self):
        """Create a tab with overall statistics."""
        widget = QWidget()
        layout = QVBoxLayout()

        # clear stats table
        self.stats_table.clear()

        # overall statistics table
        self.stats_table.setColumnCount(6)
        self.stats_table.setHorizontalHeaderLabels(["Layer", "Type", "Relay Counts", "Max Count", "Mean Count", "Total Count"])

        # combine logical and physical layers into a unified dataset
        all_layers = []

        # logical layers statistics
        for subunit in self.parsed_data.get("subunits", []):
            name = f"Subunit {subunit['layer_id']}"
            type = f"{subunit['description']}"
            relay_counts = list(subunit["relays"].values())
            max_count = max(relay_counts, default=0)
            mean_count = round(sum(relay_counts) / len(relay_counts), 2) if relay_counts else 0
            sum_counts = round(sum(relay_counts)) if len(relay_counts) > 1 else 0
            all_layers.append([name, type, relay_counts, max_count, mean_count, sum_counts])

        # physical layers statistics
        for loop in self.parsed_data.get("physical_layers", []):
            name = f"Loop {loop['loop_id']}"
            type = f"Physical"
            relay_counts = list(loop["relays"].values())
            max_count = max(relay_counts, default=0)
            mean_count = round(sum(relay_counts) / len(relay_counts), 2) if relay_counts else 0
            sum_counts = round(sum(relay_counts)) if len(relay_counts) > 1 else 0
            all_layers.append([name, type, relay_counts, max_count, mean_count, sum_counts])

        # populate the table
        self.stats_table.setRowCount(len(all_layers))
        for row, layer_stats in enumerate(all_layers):
            for col, value in enumerate(layer_stats):
                self.stats_table.setItem(row, col, QTableWidgetItem(str(value)))

        # signal & slot connection
        self.stats_table.itemSelectionChanged.connect(self.on_statistics_row_selected)

        # add the table to the layout
        layout.addWidget(self.stats_table)

        # add overall graph
        canvas = self.create_overall_graph()
        layout.addWidget(canvas)

        widget.setLayout(layout)
        return widget
    
    def create_overall_graph(self):
        """Create an overall graph for relay counts."""
        fig = Figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        layers = self.parsed_data.get("subunits", []) + self.parsed_data.get("physical_layers", [])
        names = [f"{layer.get('layer_id', layer.get('loop_id'))}" for layer in layers]
        counts = [sum(layer["relays"].values(), 0) for layer in layers]

        ax.bar(names, counts, color="blue", alpha=0.7)
        ax.set_title("Total Relay Counts by Layer")
        ax.set_xlabel("Layer")
        ax.set_ylabel("Total Count")

        return canvas

    def get_all_relay_counts(self):
        """Aggregate all relay counts from logical and physical layers."""
        counts = []
        for subunit in self.parsed_data.get("subunits", []):
            counts.extend(subunit["relays"].values())
        for loop in self.parsed_data.get("physical_layers", []):
            counts.extend(loop["relays"].values())
        return counts

    def get_top_relays(self, layer_type):
        """Get the top 5 relays by count."""
        relays = []
        if layer_type == "logical":
            for subunit in self.parsed_data.get("subunits", []):
                relays.extend(subunit["relays"].keys())
        elif layer_type == "physical":
            for loop in self.parsed_data.get("physical_layers", []):
                relays.extend(loop["relays"].keys())
        return sorted(relays, reverse=True)[:5]

    def create_graph(self):
        """Create a graph canvas."""
        fig = Figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        relay_counts = self.get_all_relay_counts()
        ax.hist(relay_counts, bins=20, color="blue", alpha=0.7)
        ax.set_title("Relay Count Distribution")
        ax.set_xlabel("Relay Count")
        ax.set_ylabel("Frequency")

        return canvas
    
    def on_statistics_row_selected(self):
        """Emit the layer name when a statistics row is selected."""
        selected_items = self.stats_table.selectedItems()
        if selected_items:
            layer_name = selected_items[0].text() # column name
            self.statistics_row_selected.emit(layer_name)

    def highlight_table_by_line(self, line_text):
        """Highlight the corresponding table cell based on the line text."""
        if line_text.startswith("R;L;"):
            match = re.match(r"R;L;S([0-9]+)BIT([0-9]+);([0-9]+)", line_text)
            if match:
                subunit_id, bit, _ = map(int, match.groups())
                for subunit in self.parsed_data.get("subunits", []):
                    if subunit["layer_id"] == subunit_id:
                        cols = subunit["cols"]
                        row = (bit - 1) // cols
                        col = (bit - 1) % cols
                        regex = rf'^Subunit {subunit_id} -.*$'
                        self.highlight_table_cell(regex, row, col)
                        break

        elif line_text.startswith("R;P;"):
            match = re.match(r"R;P;L([0-9]+)BIT([0-9]+);([0-9]+)", line_text)
            if match:
                loop_id, bit, _ = map(int, match.groups())
                for loop in self.parsed_data.get("physical_layers", []):
                    if loop["loop_id"] == loop_id:
                        regex = rf'^Loop {loop_id} -.*$'
                        self.highlight_table_cell(regex, bit - 1, 0)
                        break

    def highlight_table_cell(self, regex, row, col):
        """Highlight a specific table cell in the given tab."""
        pattern = re.compile(regex)
        for index in range(self.tab_widget.count()):
            tab_name = self.tab_widget.tabText(index)
            if pattern.match(tab_name):  # match the regex with the tab name
                self.tab_widget.setCurrentIndex(index)
                table = self.tab_widget.widget(index).findChild(QTableWidget)
                if table:
                    table.setCurrentCell(row, col)
                    table.scrollToItem(table.item(row, col))  # ensure the cell is visible
                    break

    def apply_heatmap_to_table(self, table, heatmap_ranges):
        """Apply heatmap colors to a specific table."""
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    value = int(item.text())
                    item.setBackground(get_heatmap_color(value, heatmap_ranges))

    def reload_heatmap(self, heatmap_ranges):
        """Reapply heatmap colors to all stored tables."""
        for table in self.tables:
            self.apply_heatmap_to_table(table, heatmap_ranges)