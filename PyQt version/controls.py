from PyQt5.QtWidgets import QGroupBox, QFormLayout, QSlider, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt


class Switch(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(40, 20)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(self.get_stylesheet(False))
        self.toggled.connect(self.on_toggled)

    def on_toggled(self, checked):
        self.setStyleSheet(self.get_stylesheet(checked))

    def get_stylesheet(self, checked):
        return '''
            QPushButton {{
                background-color: {color};
                border-radius: 10px;
            }}
            QPushButton::indicator {{
                width: 20px;
                height: 20px;
                background-color: white;
                border-radius: 10px;
                position: absolute;
                {position}: 2px;
                transition: all 0.3s;
            }}
        '''.format(color='#4caf50' if checked else '#ccc', position='right' if checked else 'left')


def create_param_group(title, label_text, min_val, max_val, default_val, slot):
    group = QGroupBox(title)
    layout = QFormLayout()
    slider = create_slider(min_val, max_val, default_val, slot)
    layout.addRow(label_text, slider)
    group.setLayout(layout)
    return group


def create_slider(min_val, max_val, default_val, slot):
    slider = QSlider(Qt.Horizontal)
    slider.setRange(min_val, max_val)
    slider.setValue(default_val)
    slider.valueChanged.connect(slot)
    return slider


def create_tab(widget):
    tab = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(widget)
    layout.addStretch()
    tab.setLayout(layout)
    return tab
