#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2024, Ondrej Vanka
# 
# File:         heatmaprange.py
# Description:  Qt Heatmap range widget
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

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSpinBox, QPushButton, QSplitter
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal

# helper func
def get_heatmap_color(value, ranges):
    """Determine the heatmap color for a given value."""
    if value == 0:
        return QColor(128, 128, 128)    # gray for no count
    elif value <= ranges[0]:
        return QColor(0, 255, 0)        # green for ok Level
    elif value <= ranges[1]:
        return QColor(255, 255, 0)      # yellow for warning Level
    else:
        return QColor(255, 0, 0)        # red for critical Level

#
# class HeatMapRange
#
class HeatMapRange(QWidget):

    range_changed = pyqtSignal(list)  # signal emitted when ranges are updated

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(420,50)
        self.setMaximumSize(1080,50)

        self.no_count_color = (128, 128, 128)  # gray
        self.ok_level_color = (0, 255, 0)  # green
        self.warning_level_color = (255, 255, 0)  # yellow
        self.critical_level_color = (255, 0, 0)  # red

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(QLabel("HeatMap Ranges"))

        # range 1: OK Level
        self.ok_spinner = QSpinBox()
        self.ok_spinner.setRange(1, 1000000000)
        self.ok_spinner.setValue(100000)  # default value
        self.layout.addWidget(QLabel("OK Level (Max)"))
        self.layout.addWidget(self.ok_spinner)

        # range 2: Warning Level
        self.warning_spinner = QSpinBox()
        self.warning_spinner.setRange(1, 1000000000)
        self.warning_spinner.setValue(100000000)  # default value
        self.layout.addWidget(QLabel("Warning Level (Max)"))
        self.layout.addWidget(self.warning_spinner)

        # connect signals
        self.ok_spinner.valueChanged.connect(self.emit_range_changed)
        self.warning_spinner.valueChanged.connect(self.emit_range_changed)

    def emit_range_changed(self):
        """Emit signal with updated ranges."""
        ranges = self.get_ranges()
        self.range_changed.emit(ranges)

    def get_ranges(self):
        """Get the current heatmap ranges."""
        return [self.ok_spinner.value(), self.warning_spinner.value()]
