#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2024, Ondrej Vanka
# 
# File:         pircviewer.py
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

from .pidbcard import PiDbCard
from .pitableview import PiTableView
from .pidbcardview import PiDbCardView
from .pidbcardlist import PiDbCardList
from .heatmaprange import HeatMapRange

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter, QFileDialog
)

import sys

class PircViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pirccua - (not)Pickering Relay Cycle Counting Utility Application")
        
        self.setMinimumSize(640,480)
        self.setMaximumSize(1920,1080)
        
        self.resize(1200, 800)

        # initialize core widgets
        self.heatmap_range_widget = HeatMapRange(self)
        self.pi_db_card_list = PiDbCardList(self)  # pass self as parent
        self.pi_db_card_view = PiDbCardView(self)
        self.pi_db_table_view = PiTableView(self.heatmap_range_widget)

        # layout management
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        splitter = QSplitter(self)

        # add widgets to splitter
        splitter.addWidget(self.pi_db_card_list)
        splitter.addWidget(self.pi_db_card_view)
        splitter.addWidget(self.pi_db_table_view)

        layout.addWidget(splitter)
        layout.addWidget(self.heatmap_range_widget)

        # signal & slots
        self.pi_db_card_view.line_selected.connect(self.on_line_selected)
        self.pi_db_table_view.cell_selected.connect(self.on_table_cell_selected)
        self.pi_db_card_list.generation_selected.connect(self.load_file_from_tree)
        self.heatmap_range_widget.range_changed.connect(self.update_heatmap)
        self.pi_db_table_view.statistics_row_selected.connect(self.switch_tab_by_layer_name)

        # file menu
        self.create_menu()

    def create_menu(self):
        """Create the File -> Open menu."""
        menu = self.menuBar().addMenu("File")

        open_action = menu.addAction("Open")
        open_action.triggered.connect(self.open_file)

        open_multiple_action = menu.addAction("Open Files")
        open_multiple_action.triggered.connect(self.open_files)

        clear_action = menu.addAction("Clear")
        clear_action.triggered.connect(self.clear_all_data)

        clear_action = menu.addAction("Exit")
        clear_action.triggered.connect(self.app_exit)

    def open_files(self):
        """Open multiple files and add them to the PiCardList."""
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open DB Files", "", "DB Files (*.db *.txt)")
        for file_path in file_paths:
            self.load_file(file_path)

    def open_file(self):
        """Open a file using a file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Card Files (*.db *.txt)")
        if file_path:
            self.load_file(file_path)

    def clear_all_data(self):
        """Clear all data and reset the application state."""
        self.pi_db_card_list.clear()
        self.pi_db_card_view.clear()
        self.pi_db_table_view.clear_tabs()

    def app_exit(self):
        """Exit the application."""
        self.close()

    def load_file_from_tree(self, file_path):
        """Load a file when a generation node is clicked in the tree."""
        parser = PiDbCard(file_path)
        parsed_data = parser.parse_file()

        # update the PiDbCardView and PiTableView with the selected file
        self.pi_db_card_view.load_file(file_path)
        self.pi_db_table_view.parsed_data = parsed_data
        self.pi_db_table_view.populate_tabs()

    def load_file(self, file_path):
        
        parser = PiDbCard(file_path)
        parsed_data = parser.parse_file()

        # add the parsed card to the list
        self.pi_db_card_list.add_card(file_path, parsed_data)

        # if the PiDbCardView and PiTableView are empty, load the first file
        if self.pi_db_table_view.parsed_data is None:
            self.pi_db_card_view.load_file(file_path)
            self.pi_db_table_view.parsed_data = parsed_data
            self.pi_db_table_view.populate_tabs()

    def on_line_selected(self, line_no):
        line_text = self.pi_db_card_view.line_mapping.get(line_no)
        if line_text:
            self.pi_db_table_view.highlight_table_by_line(line_text)

    def on_table_cell_selected(self, relay_line):
        for idx in range(self.pi_db_card_view.count()):
            if self.pi_db_card_view.item(idx).text() == relay_line:
                self.pi_db_card_view.setCurrentRow(idx)
                break

    def switch_tab_by_layer_name(self, layer_name):
        """Switch to the tab corresponding to the selected layer."""
        for index in range(self.pi_db_table_view.tab_widget.count()):
            tab_name = self.pi_db_table_view.tab_widget.tabText(index)
            if layer_name in tab_name:  # match layer name in tab name
                self.pi_db_table_view.tab_widget.setCurrentIndex(index)
                break

    def update_heatmap(self, ranges):
        """Update the heatmap in all table views."""
        self.pi_db_table_view.reload_heatmap(ranges)