#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2024, Ondrej Vanka
# 
# File:         pidbcardviewer.py
# Description:  Qt Pi Database File Card Viewer in QList Widget
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

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal

#
# class DbCardView
#
class PiDbCardView(QListWidget):
    
    line_selected = pyqtSignal(int)  # signal emitted when a line is selected

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(240,420)
        self.setMaximumSize(240,980)

        self.line_mapping = {}
        

    def load_file(self, file_path):
        self.clear()
        self.line_mapping.clear()
        with open(file_path, 'r') as file:
            for idx, line in enumerate(file.readlines()):
                item = line.strip()
                self.addItem(item)
                self.line_mapping[idx] = line

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        item = self.itemAt(event.pos())
        if item:
            line_no = self.row(item)
            self.line_selected.emit(line_no)

    def highlight_line(self, line_no):
        """Highlight a specific line in the QListWidget."""
        if 0 <= line_no < self.list_widget.count():
            self.list_widget.setCurrentRow(line_no)
            self.list_widget.scrollToItem(self.list_widget.item(line_no))

    def connect_signals(self):
        """Connect signals to emit the line selected."""
        self.list_widget.currentRowChanged.connect(self.line_selected.emit)
