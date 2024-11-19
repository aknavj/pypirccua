#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2024, Ondrej Vanka
# 
# File:         pidbcardthreaded.py
# Description:  *.db (Database) PXI Card data structure parser Thread
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
from PyQt5.QtCore import QObject, QThread, pyqtSignal

#
# class DbCardThreaded
#
class PiDbCardThreaded(QObject):

    processing_started = pyqtSignal()
    processing_finished = pyqtSignal(dict)
    processing_error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def process_card(self):
        """Run the card processing logic."""
        self.processing_started.emit()
        try:
            parser = PiDbCard(self.file_path)
            parsed_data = parser.parse_file()
            self.processing_finished.emit(parsed_data)
        except Exception as e:
            self.processing_error.emit(str(e))