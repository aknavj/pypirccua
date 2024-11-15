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


class FileDisplayPanel(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Store a reference to the FileComparator
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
        file_path, _ = QFileDialog.getOpenFileName(self, f"Open {self.title}", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            self.label.setText(f"{self.title}: {file_path}")
            parser = CardParser(file_path)
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

        # Add logical subunits
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

        # Add physical loops
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

        # Logical subunits
        for subunit in self.parsed_data.get("subunits", []):
            relay_counts = list(subunit["relays"].values())
            rows, cols = subunit["rows"], subunit["cols"]

            max_switch_operations = max(relay_counts, default=0)

            # Top 5 BIT numbers with highest counts
            top_5_relays = sorted(subunit["relays"].items(), key=lambda x: x[1], reverse=True)[:5]
            top_5_bits = [f"Bit ({row+1}, {col+1})" for (row, col), _ in top_5_relays]

            mean_operations = round(sum(relay_counts) / len(relay_counts), 2) if relay_counts else 0

            # Additional metrics
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

        # Physical loops
        for loop in self.parsed_data.get("physical_layers", []):
            relay_counts = list(loop["relays"].values())
            rows = loop["rows"]

            max_switch_operations = max(relay_counts, default=0)

            # Top 5 BIT numbers with highest counts
            top_5_relays = sorted(loop["relays"].items(), key=lambda x: x[1], reverse=True)[:5]
            top_5_bits = [f"Bit {row+1}" for (row, _), _ in top_5_relays]

            mean_operations = round(sum(relay_counts) / len(relay_counts), 2) if relay_counts else 0

            # Additional metrics
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



class FileComparator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("(not)Pickering Relay Cycle Counting Utility Application")
        self.resize(1200, 800)

        self.main_layout = QSplitter(Qt.Horizontal)
        self.file1_panel = FileDisplayPanel("File 1", parent=self)
        self.file2_panel = FileDisplayPanel("File 2", parent=self)
        self.main_layout.addWidget(self.file1_panel)
        self.main_layout.addWidget(self.file2_panel)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.main_layout)

        compare_button = QPushButton("Compare")
        compare_button.clicked.connect(self.compare_files)
        layout.addWidget(compare_button)

        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        layout.addWidget(self.summary)

        container.setLayout(layout)
        self.setCentralWidget(container)

        self.create_menu()


    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_file1_action = QAction("Open File 1", self)
        open_file1_action.triggered.connect(lambda: self.file1_panel.load_file())
        file_menu.addAction(open_file1_action)

        open_file2_action = QAction("Open File 2", self)
        open_file2_action.triggered.connect(lambda: self.file2_panel.load_file())
        file_menu.addAction(open_file2_action)

    def compare_files(self):
        if not self.file1_panel.parsed_data or not self.file2_panel.parsed_data:
            self.summary.setText("Both files must be loaded to compare.")
            return

        differences = self.calculate_differences()
        self.summary.setText(differences)

    def calculate_differences(self):
        file1_data = self.file1_panel.parsed_data
        file2_data = self.file2_panel.parsed_data

        if not file1_data or not file2_data:
            return "No data to compare."

        summary = []

        # Compare Logical Subunits
        subunit_differences = self.compare_subunits(file1_data.get("subunits", []), file2_data.get("subunits", []))
        summary.append(f"Logical Subunits: {subunit_differences['summary']}")

        # Compare Physical Loops
        loop_differences = self.compare_physical_loops(file1_data.get("physical_layers", []), file2_data.get("physical_layers", []))
        summary.append(f"Physical Loops: {loop_differences['summary']}")

        return "\n".join(summary)

    def compare_subunits(self, subunits1, subunits2):
        differences = {"matches": 0, "mismatches": 0}
        for subunit1, subunit2 in zip(subunits1, subunits2):
            for (row, col), value1 in subunit1["relays"].items():
                value2 = subunit2["relays"].get((row, col), 0)
                if value1 == value2:
                    differences["matches"] += 1
                else:
                    differences["mismatches"] += 1

        total = differences["matches"] + differences["mismatches"]
        summary = f"{differences['matches']} matches, {differences['mismatches']} mismatches ({total} total)."
        return {"summary": summary}

    def compare_physical_loops(self, loops1, loops2):
        differences = {"matches": 0, "mismatches": 0}
        for loop1, loop2 in zip(loops1, loops2):
            for (row, _), value1 in loop1["relays"].items():
                value2 = loop2["relays"].get((row, 0), 0)
                if value1 == value2:
                    differences["matches"] += 1
                else:
                    differences["mismatches"] += 1

        total = differences["matches"] + differences["mismatches"]
        summary = f"{differences['matches']} matches, {differences['mismatches']} mismatches ({total} total)."
        return {"summary": summary}


if __name__ == "__main__":
    app = QApplication(sys.argv)
    comparator = FileComparator()
    comparator.show()
    sys.exit(app.exec_())
