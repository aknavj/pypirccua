from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal

# txt view
class PiDbCardView(QListWidget):
    
    line_selected = pyqtSignal(int)  # signal emitted when a line is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_mapping = {}
        
        #self.layout = QVBoxLayout()
        #self.list_widget = QListWidget()
        #self.layout.addWidget(self.list_widget)
        #self.setLayout(self.layout)

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
