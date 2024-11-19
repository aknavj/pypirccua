#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2024, Ondrej Vanka
# 
# File:         pircviewer.py
# Description:  Qt PiRc Viewer - main app
# Version:      1.08
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
from .pidbcardthreaded import PiDbCardThreaded

from PyQt5.QtCore import QThread, Qt, QSettings
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QSplitter, QFileDialog, QStatusBar, QProgressBar
)

import sys

#
# class PircViewer main window
#
class PircViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.current_thread = None  # track the current processing thread

        self.setWindowTitle("pypirccua - Pickering Relay Cycle Counting Utility Application")
        
        self.setMinimumSize(640,480)
        self.setMaximumSize(1920,1080)
        
        self.resize(1200, 800)

        # initialize core widgets
        self.heatmap_range_widget = HeatMapRange(self)
        self.pi_db_card_list = PiDbCardList(self)  # pass self as parent
        self.pi_db_card_view = PiDbCardView(self)
        self.pi_db_table_view = PiTableView(self.heatmap_range_widget)

        self.status_bar = QStatusBar()
        self.progress_bar = QProgressBar(self)

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
        layout.addWidget(self.progress_bar)
        self.setStatusBar(self.status_bar)

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

        # file menu
        menu = self.menuBar().addMenu("File")

        open_action = menu.addAction("Open")
        open_action.triggered.connect(self.open_file)

        open_multiple_action = menu.addAction("Open Files")
        open_multiple_action.triggered.connect(self.open_files)

        # draft w.i.p - uncommented from users access
        #export_action = menu.addAction("Export")
        #export_action.triggered.connect(self.export_to_csv)

        clear_action = menu.addAction("Clear")
        clear_action.triggered.connect(self.clear_all_data)

        clear_action = menu.addAction("Exit")
        clear_action.triggered.connect(self.app_exit)

        # edit menu 
        # draft w.i.p - uncommented from users access
        #edit_menu = self.menuBar().addMenu("Edit")
        #settings_action = edit_menu.addAction("Settings")
        #settings_action.triggered.connect(self.show_settings_dialog)

        # help menu
        help_menu = self.menuBar().addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)

    def open_files(self):
        """Open multiple files and add them to the PiCardList."""
        self.progress_bar.reset()
        
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open DB Files", "", "DB Files (*.db *.txt)")
        if not file_paths:
            return  # user canceled the save dialog

        num_files = len(file_paths)

        self.progress_bar.setMaximum(num_files)

        for i in range(0,num_files):
            filename = file_paths[i]

            self.load_file(file_paths[i])

            self.progress_bar.setValue(i)
            self.statusBar().showMessage(f"File loaded successfully: {filename}", 5000)

        self.statusBar().showMessage(f"Files loaded: {int(num_files)}", 5000)
        self.progress_bar.setValue(self.progress_bar.maximum())

    def open_file(self):
        """Open a file using a file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Card Files (*.db *.txt)")
        if file_path:
            self.load_file(file_path)

    def clear_all_data(self):
        """Clear all data and reset the application state."""
        self.pi_db_card_list.remove_all_cards()
        self.pi_db_card_view.clear()
        self.pi_db_table_view.clear_tabs()
        self.progress_bar.reset()
        self.statusBar().showMessage("")

    def app_exit(self):
        """Exit the application."""
        self.close()

    def load_file_from_tree(self, file_path):
        """Load a file when a generation node is clicked in the tree."""
        self.statusBar().showMessage(f"Loading file... {file_path}", 5000)

        if self.current_thread:
            self.current_thread.quit()
            self.current_thread.wait()

        self.current_thread = QThread()
        self.card_processor = PiDbCardThreaded(file_path)
        self.card_processor.moveToThread(self.current_thread)

        # connect signals
        self.current_thread.started.connect(self.card_processor.process_card)
        self.card_processor.processing_started.connect(lambda: self.statusBar().showMessage(f"Processing file... {file_path}", 5000))
        self.card_processor.processing_finished.connect(self.on_processing_finished)
        self.card_processor.processing_error.connect(self.on_processing_error)
        self.card_processor.processing_finished.connect(self.current_thread.quit)
        self.card_processor.processing_error.connect(self.current_thread.quit)

        # start the thread
        self.current_thread.start()

    def load_file(self, file_path):
        """Handle file load."""
        # extract data and add card into list
        # todo optimize it because there is 'double call'
        parser = PiDbCard(file_path)
        parsed_data = parser.parse_file()
        self.pi_db_card_list.add_card(file_path, parsed_data)

        # ensure any previous thread is cleaned up
        if self.current_thread:
            self.current_thread.quit()
            self.current_thread.wait()

        self.current_thread = QThread()
        self.card_processor = PiDbCardThreaded(file_path)
        self.card_processor.moveToThread(self.current_thread)

        # connect signals
        self.current_thread.started.connect(self.card_processor.process_card)
        self.card_processor.processing_started.connect(lambda: self.statusBar().showMessage(f"Processing file... {file_path}", 5000))
        self.card_processor.processing_finished.connect(self.on_processing_finished)
        self.card_processor.processing_error.connect(self.on_processing_error)
        self.card_processor.processing_finished.connect(self.current_thread.quit)
        self.card_processor.processing_error.connect(self.current_thread.quit)

        # start the thread
        self.current_thread.start()

    def on_processing_finished(self, parsed_data):
        """Handle the parsed data and update the UI."""
        #clear data
        self.pi_db_card_view.clear()
        self.pi_db_table_view.clear()

        _file_path = self.card_processor.file_path
        _parsed_data = parsed_data

        self.pi_db_card_view.load_file(_file_path)
        self.pi_db_table_view.parsed_data = _parsed_data
        self.pi_db_table_view.populate_tabs()
        self.statusBar().showMessage(f"File Loaded... {_file_path}", 5000)

    def on_processing_error(self, error_message):
        """Handle errors during processing."""
        QMessageBox.critical(self, "Processing Error", f"An error occurred: {error_message}")
        self.statusBar().clearMessage()
        self.progress_bar.reset()

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

    def export_to_csv(self):
        """Call the export_to_csv method from PiTableView."""
        self.pi_db_table_view.export_to_csv()

    def show_about_dialog(self):
        about_dialog = PircAboutDialog(self)
        about_dialog.exec_()

    def show_settings_dialog(self):
        settings_dialog = PircSettingsDialog(self)
        settings_dialog.exec_()

#
# class Settings dialog
#
class PircSettingsDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 200)

        self.settings = QSettings("PyPiRCCUA", "Settings")  # QSettings for storing settings

        # Layout for the dialog
        layout = QVBoxLayout()

        # Path to PILPXIDB
        layout.addLayout(self.create_path_row("Path to PILPXIDB:", "path_pilpxidb"))

        # Path to PILLXIDB
        layout.addLayout(self.create_path_row("Path to PILLXIDB:", "path_pillxidb"))

        # Path to eBIRST dataset
        layout.addLayout(self.create_path_row("Path to eBIRST dataset:", "path_ebirst"))

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_path_row(self, label_text, setting_key):
        """Create a row with a label, a QLineEdit, and a Browse button."""
        row_layout = QHBoxLayout()
        label = QLabel(label_text)
        edit = QLineEdit()
        edit.setText(self.settings.value(setting_key, ""))
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(lambda: self.browse_folder(edit))
        row_layout.addWidget(label)
        row_layout.addWidget(edit)
        row_layout.addWidget(browse_button)

        # Store the QLineEdit and its setting key for saving later
        setattr(self, f"{setting_key}_edit", edit)
        return row_layout

    def browse_folder(self, line_edit):
        """Open a directory selection dialog and set the selected path."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            line_edit.setText(folder)

    def save_settings(self):
        """Save settings to QSettings."""
        self.settings.setValue("path_pilpxidb", self.path_pilpxidb_edit.text())
        self.settings.setValue("path_pillxidb", self.path_pillxidb_edit.text())
        self.settings.setValue("path_ebirst", self.path_ebirst_edit.text())
        self.accept()  # Close the dialog after saving

#
# class About dialog
#
class PircAboutDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About PyPiRCCUA")
        self.setFixedSize(600, 300)

        # Layout for the dialog
        layout = QVBoxLayout()

        # Application Information
        about_text = QLabel(
            """
            <h2>Python Pickering Relay Cycle Counting Utility Application</h2>
            <p>A PyQt-based application for visualizing and analyzing relay counts from DB files from Pickering PXI cards.</p>
            <p>Version: 1.1.0</p>
            <p>Author: Ondrej Vanka</p>
            <p>Contact: ondrej@vanka.net</p>
            <p>
                <a href="https://github.com/aknavj/pypirccua">GitHub Repository</a>
            </p>
            <p>
                <a href="https://pypi.org/project/pypirccua">PYPI Package</a>
            </p>
            <p>License: GNU/GPL</p>
            """
        )
        about_text.setOpenExternalLinks(True)
        about_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(about_text)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        # Apply layout
        self.setLayout(layout)