from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QScrollArea, QTabWidget, QFormLayout, QFileDialog, QAction, QMessageBox, QPushButton)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from controls import Switch, create_param_group, create_tab
from video_processing import VideoThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Video Effects")
        self.disply_width = 640
        self.display_height = 480
        self.thread = VideoThread()

        self.initUI()
        self.initMenu()
        self.show()

        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.recording_status_signal.connect(
            self.update_recording_status)
        self.thread.start()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)

        self.start_button = QPushButton("Start Recording")
        self.start_button.clicked.connect(self.start_recording)

        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.clicked.connect(self.stop_recording)

        self.capture_button = QPushButton("Capture Screenshot")
        self.capture_button.clicked.connect(self.capture_screenshot)

        self.draw_button = QPushButton("Enable Drawing")
        self.draw_button.setCheckable(True)
        self.draw_button.clicked.connect(self.toggle_drawing)

        self.recording_status = QLabel("Not Recording")

        self.effect_group_box = self.create_effects_group()
        _, param_scroll = self.create_param_widget()

        # Layout des boutons de contrôle
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.capture_button)
        button_layout.addWidget(self.draw_button)
        button_layout.addWidget(self.recording_status)

        # Layout principal horizontal
        main_layout = QHBoxLayout()
        control_layout = QVBoxLayout()
        control_layout.addWidget(self.effect_group_box)
        control_layout.addWidget(param_scroll)
        control_layout.addLayout(button_layout)
        control_layout.addStretch()

        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.image_label)

        central_widget.setLayout(main_layout)

        self.update_param_visibility()
        self.apply_styles()

    def create_effects_group(self):
        effect_group_box = QGroupBox("Select Effects")
        effects = ["Deformation", "Mirror", "Color Change", "Fun Filters", "Bubble", "Wave", "Pointillism",
                "Face Morphing", "Rainbow", "Glitch", "Hand Tracking", "Background Distortion", "Face Mask"]
        effect_layout = QVBoxLayout()
        self.effect_switches = {}

        for effect in effects:
            layout = QHBoxLayout()
            switch = Switch()
            switch.toggled.connect(self.on_checkbox_toggled)
            label = QLabel(effect)
            self.effect_switches[effect] = switch
            layout.addWidget(label)
            layout.addWidget(switch)
            layout.addStretch()
            effect_layout.addLayout(layout)

        effect_group_box.setLayout(effect_layout)
        return effect_group_box

    def create_param_widget(self):
        self.deformation_intensity_slider = create_param_group(
            "Deformation Parameters", "Deformation Intensity", 1, 10, 1, self.on_deformation_intensity_changed)
        self.pointillism_size_slider = create_param_group(
            "Pointillism Parameters", "Pointillism Size", 1, 10, 2, self.on_pointillism_size_changed)
        self.facemask_point_size_slider = create_param_group(
            "Face Mask Parameters", "Face Mask Point Size", 1, 20, 5, self.on_facemask_point_size_changed)
        self.mirror_effect_intensity_slider = create_param_group(
            "Mirror Parameters", "Mirror Intensity", 1, 10, 1, self.on_mirror_intensity_changed)

        param_layout = QVBoxLayout()
        param_layout.addWidget(self.deformation_intensity_slider)
        param_layout.addWidget(self.pointillism_size_slider)
        param_layout.addWidget(self.facemask_point_size_slider)
        param_layout.addWidget(self.mirror_effect_intensity_slider)
        param_layout.addStretch()

        param_widget = QWidget()
        param_widget.setLayout(param_layout)
        param_scroll = QScrollArea()
        param_scroll.setWidgetResizable(True)
        param_scroll.setWidget(param_widget)

        return param_widget, param_scroll

    def initMenu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        help_menu = menubar.addMenu("Help")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        about_text = (
            "Interactive Video Effects Application\n\n"
            "This application allows you to apply various real-time effects "
            "to video streams using advanced tracking and processing techniques. "
            "You can select different effects and adjust their parameters to see "
            "the changes live.\n\n"
            "Features:\n"
            "- Deformation\n"
            "- Mirror\n"
            "- Color Change\n"
            "- Fun Filters\n"
            "- Bubble\n"
            "- Wave\n"
            "- Pointillism\n"
            "- Face Morphing\n"
            "- Rainbow\n"
            "- Glitch\n"
            "- Hand Tracking\n"
            "- Background Distortion\n"
            "- Face Mask\n\n"
            "Developed by Nathan Chambrette"
        )
        QMessageBox.about(self, "About", about_text)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def update_image(self, frame):
        qt_image = self.convert_cv_qt(frame)
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    def update_recording_status(self, is_recording):
        self.recording_status.setText(
            "Recording" if is_recording else "Not Recording")

    @pyqtSlot()
    def on_checkbox_toggled(self):
        selected_effects = [
            effect for effect, switch in self.effect_switches.items() if switch.isChecked()]
        self.thread.selected_effects = selected_effects
        self.update_param_visibility()

    def on_deformation_intensity_changed(self, value):
        self.thread.deformation_intensity = value

    def on_pointillism_size_changed(self, value):
        self.thread.pointillism_size = value

    def on_facemask_point_size_changed(self, value):
        self.thread.facemask_point_size = value

    def on_mirror_intensity_changed(self, value):
        self.thread.mirror_intensity = value

    def capture_screenshot(self):
        screenshot = self.image_label.pixmap()
        if screenshot:
            options = QFileDialog.Options()
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Screenshot", "", "PNG Files (*.png);;All Files (*)", options=options)
            if filename:
                screenshot.save(filename)

    def start_recording(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Video", "", "AVI Files (*.avi);;All Files (*)", options=options)
        if filename:
            self.thread.start_recording(filename)

    def stop_recording(self):
        self.thread.stop_recording()

    def toggle_drawing(self):
        self.thread.drawing = self.draw_button.isChecked()
        self.draw_button.setText(
            "Disable Drawing" if self.thread.drawing else "Enable Drawing")

    def update_param_visibility(self):
        effects_requiring_params = {
            "Deformation": ["deformation_intensity_slider"],
            "Pointillism": ["pointillism_size_slider"],
            "Face Mask": ["facemask_point_size_slider"],
            "Mirror": ["mirror_effect_intensity_slider"]
        }

        visible_params = set()
        for effect in self.thread.selected_effects:
            if effect in effects_requiring_params:
                visible_params.update(effects_requiring_params[effect])

        for param_name in ["deformation_intensity_slider", "pointillism_size_slider", "facemask_point_size_slider", "mirror_effect_intensity_slider"]:
            param_widget = getattr(self, param_name)
            param_widget.setVisible(param_name in visible_params)

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(
            rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QImage(convert_to_qt_format)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QGroupBox {
                background-color: #34495e;
                border: 1px solid #2c3e50;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                background-color: #2c3e50;
            }
            QRadioButton, QCheckBox, QPushButton {
                background-color: #34495e;
                border: none;
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #1abc9c;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
            QLabel {
                padding: 5px;
            }
            QDial, QSlider {
                background-color: #34495e;
                border: 1px solid #2c3e50;
                border-radius: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #2c3e50;
                background-color: #34495e;
            }
            QTabBar::tab {
                background: #34495e;
                color: #ecf0f1;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: #1abc9c;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
