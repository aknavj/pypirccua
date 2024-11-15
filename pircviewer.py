from pitableview import *
from pidbcardview import *

from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QSplitter, QFileDialog, QMenuBar, QAction
)

import sys

#
# App main window
#
class PircViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pirccua - (not)Pickering Relay Cycle Counting Utility Application")
        self.resize(1200, 800)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        top_splitter = QSplitter(Qt.Horizontal)

        # heatmap widget
        self.heatmap_range_widget = HeatMapRange()

        # fileviewer
        self.file_view = PiDbCardView()
        top_splitter.addWidget(self.file_view)

        # tableviewer
        self.viewer_panel = PiTableView(self.heatmap_range_widget)
        top_splitter.addWidget(self.viewer_panel)

        top_splitter.setSizes([400, 800])  # Adjust initial sizes
        main_layout.addWidget(top_splitter)

        main_layout.addWidget(self.heatmap_range_widget)

        # signals&slots
        self.file_view.line_selected.connect(self.on_line_selected)
        self.viewer_panel.cell_selected.connect(self.on_table_cell_selected)
        self.heatmap_range_widget.update_button.clicked.connect(self.update_heatmap)

        self.create_menu()

    def create_menu(self):
        """Create the File -> Open menu."""
        menu = self.menuBar().addMenu("File")
        open_action = menu.addAction("Open")
        open_action.triggered.connect(self.open_file)

    def open_file(self):
        """Open a file using a file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Card Files (*.db *.txt)")
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        """Load a file and update views."""
        self.file_view.load_file(file_path)
        parser = PiDbCard(file_path)
        parsed_data = parser.parse_file()
        self.viewer_panel.parsed_data = parsed_data
        self.viewer_panel.populate_tabs()

    def on_line_selected(self, line_no):
        line_text = self.file_view.line_mapping.get(line_no)
        if line_text:
            self.viewer_panel.highlight_table_by_line(line_text)

    def on_table_cell_selected(self, relay_line):
        for idx in range(self.file_view.count()):
            if self.file_view.item(idx).text() == relay_line:
                self.file_view.setCurrentRow(idx)
                break

    def update_heatmap(self):
        """Update heatmap colors in all tables."""
        self.viewer_panel.populate_tabs()


    #def create_menu(self):
    #    menu_bar = self.menuBar()
    #    file_menu = menu_bar.addMenu("File")
    #
    #    open_file1_action = QAction("Open File 1", self)
    #    open_file1_action.triggered.connect(lambda: self.file1_panel.load_file())
    #    file_menu.addAction(open_file1_action)
    #
    #    open_file2_action = QAction("Open File 2", self)
    #    open_file2_action.triggered.connect(lambda: self.file2_panel.load_file())
    #    file_menu.addAction(open_file2_action)

    #def compare_files(self):
    #    if not self.file1_panel.parsed_data or not self.file2_panel.parsed_data:
    #        self.summary.setText("Both files must be loaded to compare.")
    #        return
    #
    #    differences = self.calculate_differences()
    #    self.summary.setText(differences)

    #def calculate_differences(self):
    #    file1_data = self.file1_panel.parsed_data
    #    file2_data = self.file2_panel.parsed_data
    #
    #    if not file1_data or not file2_data:
    #        return "No data to compare."
    #
    #    summary = []
    #
    #    # compare logical Subunits
    #    subunit_differences = self.compare_subunits(file1_data.get("subunits", []), file2_data.get("subunits", []))
    #    summary.append(f"Logical Subunits: {subunit_differences['summary']}")
    #
    #    # compare physical Loops
    #    loop_differences = self.compare_physical_loops(file1_data.get("physical_layers", []), file2_data.get("physical_layers", []))
    #    summary.append(f"Physical Loops: {loop_differences['summary']}")
    #
    #    return "\n".join(summary)

    #def compare_subunits(self, subunits1, subunits2):
    #    differences = {"matches": 0, "mismatches": 0}
    #    for subunit1, subunit2 in zip(subunits1, subunits2):
    #        for (row, col), value1 in subunit1["relays"].items():
    #            value2 = subunit2["relays"].get((row, col), 0)
    #            if value1 == value2:
    #                differences["matches"] += 1
    #            else:
    #                differences["mismatches"] += 1
    #
    #    total = differences["matches"] + differences["mismatches"]
    #    summary = f"{differences['matches']} matches, {differences['mismatches']} mismatches ({total} total)."
    #    return {"summary": summary}

    #def compare_physical_loops(self, loops1, loops2):
    #    differences = {"matches": 0, "mismatches": 0}
    #    for loop1, loop2 in zip(loops1, loops2):
    #        for (row, _), value1 in loop1["relays"].items():
    #            value2 = loop2["relays"].get((row, 0), 0)
    #            if value1 == value2:
    #                differences["matches"] += 1
    #            else:
    #                differences["mismatches"] += 1
    #
    #    total = differences["matches"] + differences["mismatches"]
    #    summary = f"{differences['matches']} matches, {differences['mismatches']} mismatches ({total} total)."
    #    return {"summary": summary}


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = PircViewer()
    wnd.show()
    sys.exit(app.exec_())
