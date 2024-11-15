from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSpinBox, QPushButton, QSplitter
from PyQt5.QtGui import QColor

# helper func
def get_heatmap_color(value, ranges):
    """Return a QColor based on the value and ranges."""
    if value == 0:
        return QColor("gray")
    elif value <= ranges["ok_max"]:
        return QColor("green")
    elif value <= ranges["warning_max"]:
        return QColor("yellow")
    else:
        return QColor("red")

# heatmap widget
class HeatMapRange(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()

        self.no_count_label = QLabel("No Count (0):")
        self.ok_level_label = QLabel("Ok Level (1 to 1000000):")
        self.warning_level_label = QLabel("Warning Level (1000000+):")
        self.critical_level_label = QLabel("Critical Level (1000000000+):")

        self.no_count_color = QLabel("Gray")
        self.ok_level_color = QLabel("Green")
        self.warning_level_color = QLabel("Yellow")
        self.critical_level_color = QLabel("Red")

        self.ok_max_spinbox = QSpinBox()
        self.warning_max_spinbox = QSpinBox()
        self.ok_max_spinbox.setValue(1000000)
        self.warning_max_spinbox.setValue(1000000000)

        self.update_button = QPushButton("Update Heatmap")

        self.layout.addWidget(self.no_count_label)
        self.layout.addWidget(self.no_count_color)
        self.layout.addWidget(self.ok_level_label)
        self.layout.addWidget(self.ok_max_spinbox)
        self.layout.addWidget(self.warning_level_label)
        self.layout.addWidget(self.warning_max_spinbox)
        self.layout.addWidget(self.critical_level_label)
        self.layout.addWidget(self.critical_level_color)
        self.layout.addWidget(self.update_button)

        self.setLayout(self.layout)

    def get_ranges(self):
        """Return the heatmap ranges."""
        return {
            "ok_max": self.ok_max_spinbox.value(),
            "warning_max": self.warning_max_spinbox.value(),
        }
