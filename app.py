from pyqt_dbtableview import *

#
# App main window
#
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("(not)Pickering Relay Cycle Counting Utility Application")
        self.resize(1200, 800)

        self.main_layout = QSplitter(Qt.Horizontal)
        self.file1_panel = DbTableView("File 1", parent=self)
        self.file2_panel = DbTableView("File 2", parent=self)
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

        # compare logical Subunits
        subunit_differences = self.compare_subunits(file1_data.get("subunits", []), file2_data.get("subunits", []))
        summary.append(f"Logical Subunits: {subunit_differences['summary']}")

        # compare physical Loops
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
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec_())
