from db_card_file import *

import sys
import re
from collections import Counter
from statistics import stdev
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter,
    QTabWidget, QFileDialog, QLabel, QTableWidget, QTableWidgetItem,
    QAction, QPushButton, QTextEdit
)
from PyQt5.QtCore import Qt

# qt db card file table view
class QtDbTableView(QWidget):

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # store a reference to the DbCardFileComparator
        self.title = title
        self.parsed_data = None
        self.layout = QVBoxLayout()
        self.label = QLabel(f"{title}: No file loaded")
        self.card_info_label = QLabel("Card Info: ")
        self.tab_widget = QTabWidget()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.card_info_label)
        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, f"Open {self.title}", "", "Text Files (*.db);;All Files (*)")
        if file_path:
            self.label.setText(f"{self.title}: {file_path}")
            parser = DbCardFile(file_path)
            self.parsed_data = parser.parse_file()
            self.populate_card_info()
            self.populate_tabs()

    def populate_card_info(self):
        if self.parsed_data and self.parsed_data.get("header"):
            header = self.parsed_data["header"]
            generation = self.parsed_data.get("generation", "N/A")
            self.card_info_label.setText(
                f"Card Info: Version {header['version']}, {header['card_info']} (Generation {generation})"
            )

    def populate_tabs(self):
        self.tab_widget.clear()
        if not self.parsed_data:
            return

        # Add statistics tab
        self.add_statistics_tab()

        is_comparing = self.parent_window and self.parent_window.file2_panel.parsed_data is not None

        # add logical subunits data
        for subunit in self.parsed_data.get("subunits", []):
            rows, cols = subunit["rows"], subunit["cols"]
            subunit_table = QTableWidget(rows, cols)
            subunit_table.setHorizontalHeaderLabels([f"Col {i+1}" for i in range(cols)])
            subunit_table.setVerticalHeaderLabels([f"Row {i+1}" for i in range(rows)])

            relays2 = {}
            if is_comparing:
                for s2 in self.parent_window.file2_panel.parsed_data.get("subunits", []):
                    if s2["layer_id"] == subunit["layer_id"]:
                        relays2 = s2["relays"]

            self.highlight_differences(subunit_table, subunit["relays"], relays2, rows, cols)
            self.tab_widget.addTab(subunit_table, f"Logical Subunit {subunit['layer_id']}")

        # add physical loops data
        for loop in self.parsed_data.get("physical_layers", []):
            rows = loop["rows"]
            loop_table = QTableWidget(rows, 1)  # Single column for relay counts
            loop_table.setHorizontalHeaderLabels(["Relay Value"])
            loop_table.setVerticalHeaderLabels([f"Bit {i+1}" for i in range(rows)])

            relays2 = {}
            if is_comparing:
                for l2 in self.parent_window.file2_panel.parsed_data.get("physical_layers", []):
                    if l2["loop_id"] == loop["loop_id"]:
                        relays2 = l2["relays"]

            self.highlight_differences(loop_table, loop["relays"], relays2, rows, 1, is_physical=True)
            self.tab_widget.addTab(loop_table, f"Physical Loop {loop['loop_id']}")

    def add_statistics_tab(self):
        stats_table = QTableWidget()
        stats_table.setColumnCount(8)
        stats_table.setHorizontalHeaderLabels([
            "Type of Layer",
            "Maximum Switch Operations",
            "5 Highest Counted Relays (BITs)",
            "Mean Operations",
            "Utilization (%)",
            "Standard Deviation",
            "Most Common Count",
            "Density"
        ])

        stats = self.calculate_statistics()
        stats_table.setRowCount(len(stats))

        for row, stat in enumerate(stats):
            for col, value in enumerate(stat):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                stats_table.setItem(row, col, item)

        self.tab_widget.addTab(stats_table, "Statistics")

    def calculate_statistics(self):
        statistics = []

        # calc logical subunits
        for subunit in self.parsed_data.get("subunits", []):
            relay_counts = list(subunit["relays"].values())
            rows, cols = subunit["rows"], subunit["cols"]

            max_switch_operations = max(relay_counts, default=0)

            # top 5 BIT numbers with highest counts
            top_5_relays = sorted(subunit["relays"].items(), key=lambda x: x[1], reverse=True)[:5]
            top_5_bits = [f"Bit ({row+1}, {col+1})" for (row, col), _ in top_5_relays]

            mean_operations = round(sum(relay_counts) / len(relay_counts), 2) if relay_counts else 0

            # additional metrics
            utilization = round((len([v for v in relay_counts if v > 0]) / (rows * cols)) * 100, 2) if relay_counts else 0
            std_dev = round(stdev(relay_counts), 2) if len(relay_counts) > 1 else 0
            most_common = Counter(relay_counts).most_common(1)
            most_common_count = most_common[0][0] if most_common else 0
            density = round(len([v for v in relay_counts if v > 0]) / (rows * cols), 2)

            statistics.append([
                f"Logical Subunit {subunit['layer_id']}",
                max_switch_operations,
                ", ".join(top_5_bits),
                mean_operations,
                utilization,
                std_dev,
                most_common_count,
                density
            ])

        # calc physical loops
        for loop in self.parsed_data.get("physical_layers", []):
            relay_counts = list(loop["relays"].values())
            rows = loop["rows"]

            max_switch_operations = max(relay_counts, default=0)

            # top 5 BIT numbers with highest counts
            top_5_relays = sorted(loop["relays"].items(), key=lambda x: x[1], reverse=True)[:5]
            top_5_bits = [f"Bit {row+1}" for (row, _), _ in top_5_relays]

            mean_operations = round(sum(relay_counts) / len(relay_counts), 2) if relay_counts else 0

            # additional metrics
            utilization = round((len([v for v in relay_counts if v > 0]) / rows) * 100, 2) if relay_counts else 0
            std_dev = round(stdev(relay_counts), 2) if len(relay_counts) > 1 else 0
            most_common = Counter(relay_counts).most_common(1)
            most_common_count = most_common[0][0] if most_common else 0
            density = round(len([v for v in relay_counts if v > 0]) / rows, 2)

            statistics.append([
                f"Physical Loop {loop['loop_id']}",
                max_switch_operations,
                ", ".join(top_5_bits),
                mean_operations,
                utilization,
                std_dev,
                most_common_count,
                density
            ])

        return statistics

    # note: not correct for now but as placeholder it suits the need...
    def highlight_differences(self, table, relays1, relays2, rows, cols, is_physical=False):
        for row in range(rows):
            for col in range(cols):
                if is_physical:
                    value1 = relays1.get((row, 0), 0)
                    value2 = relays2.get((row, 0), 0)
                else:
                    value1 = relays1.get((row, col), 0)
                    value2 = relays2.get((row, col), 0)

                item = QTableWidgetItem(str(value1))
                if value1 == value2:
                    item.setBackground(Qt.green)
                elif abs(value1 - value2) <= 10:
                    item.setBackground(Qt.yellow)
                else:
                    item.setBackground(Qt.red)
                table.setItem(row, col, item)
