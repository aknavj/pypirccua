#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2024, Ondrej Vanka
# 
# File:         pidbcardlist.py
# Description:  Qt Pi Database CardList widget treebox view
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

from PyQt5.QtWidgets import QMessageBox, QTreeWidget, QTreeWidgetItem, QFileDialog, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal

#
# class DbCardList
#
class PiDbCardList(QTreeWidget):
    
    generation_selected = pyqtSignal(str)  # signal to emit the file path

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(160,420)
        self.setMaximumSize(280,980)

        self.setColumnCount(1)
        self.setHeaderLabels(["PXI Cards"])
        self.cards = {}  # dictionary to store card nodes by (Card ID, Card S/N)

    def add_card(self, file_path, card_data):
        if not card_data or "header" not in card_data or "generation" not in card_data:
            QMessageBox.warning(self, "Invalid Card Data", "The provided card data is incomplete or invalid.")
            return

        header = card_data["header"]
        generation = card_data["generation"]
        card_id = header.get("card_id", "Unknown")
        card_sn = header.get("card_sn", "Unknown")
        key = (card_id, card_sn, generation)

        # check for duplicates
        if key in self.cards:
            QMessageBox.information(
                self,
                "Duplicate Card",
                f"The card [{card_id}] with S/N [{card_sn}] and Generation [{generation}] is already in the list.",
            )
            return

        # if no duplicates... add card to list
        card_node = QTreeWidgetItem(self, [f"PXI Card [{card_id}] [S/N: {card_sn}]"])
        self.addTopLevelItem(card_node)
        self.cards[key] = card_node

        generation_node = QTreeWidgetItem(card_node, [f"Generation: {generation}"])
        db_path_item = QTreeWidgetItem(generation_node, [f"Db path: {file_path}"])
        generation_node.addChild(db_path_item)
        card_node.addChild(generation_node)

        self.itemClicked.connect(self.on_item_clicked)

    def remove_card(self):
        """Remove the selected card and its data."""
        selected_item = self.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Remove Card", "No card selected to remove.")
            return

        # find the card node to remove
        if selected_item.parent() is None:  # top-level card node
            card_id_sn = selected_item.text(0).split("[")[1].split("]")[0]
            for key in list(self.cards.keys()):
                if f"{key[0]}] [S/N: {key[1]}" in card_id_sn:
                    self.takeTopLevelItem(self.indexOfTopLevelItem(selected_item))
                    del self.cards[key]
                    QMessageBox.information(self, "Remove Card", f"Card {key} removed successfully.")
                    return

        QMessageBox.warning(self, "Remove Card", "The selected item is not a valid card node.")

    def remove_all_cards(self):
        """Remove all cards from the list."""
        self.clear()
        self.cards.clear()
        QMessageBox.information(self, "Remove All Cards", "All cards have been removed successfully.")

    def on_item_clicked(self, item, column):
        if item.parent() and "Generation: " in item.text(0):
            db_path_item = item.child(0)
            if db_path_item and "Db path: " in db_path_item.text(0):
                file_path = db_path_item.text(0).replace("Db path: ", "")
                self.generation_selected.emit(file_path)  # emit the file path
