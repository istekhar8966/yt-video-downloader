import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QListWidget, QFileDialog, QProgressBar, QTabWidget,
    QCheckBox, QTextEdit, QComboBox, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt
from downloader import DownloadManager
from history import HistoryDB
from settings import SettingsManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern yt-dlp Downloader")
        self.resize(900, 600)

        self.settings = SettingsManager()
        self.history_db = HistoryDB()
        self.downloader = DownloadManager()

        self.dark_mode = self.settings.get("dark_mode", False)
        self.download_path = Path(self.settings.get("download_path", str(Path.home() / "Downloads")))

        self._init_ui()
        self.apply_theme(self.dark_mode)
        self.load_history()

        self.downloader.progress_updated.connect(self.on_progress_update)
        self.downloader.download_finished.connect(self.on_download_finished)
        self.downloader.download_error.connect(self.on_download_error)

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        sidebar = QVBoxLayout()
        sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.btn_home = QPushButton("Home")
        self.btn_history = QPushButton("History")
        self.btn_settings = QPushButton("Settings")
        for btn in [self.btn_home, self.btn_history, self.btn_settings]:
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            sidebar.addWidget(btn)

        self.btn_home.setChecked(True)

        self.tabs = QTabWidget()
        self.tabs.tabBar().hide()

        self.tab_home = QWidget()
        self._build_home_tab()
        self.tabs.addTab(self.tab_home, "Home")

        self.tab_history = QWidget()
        self._build_history_tab()
        self.tabs.addTab(self.tab_history, "History")

        self.tab_settings = QWidget()
        self._build_settings_tab()
        self.tabs.addTab(self.tab_settings, "Settings")

        self.btn_home.clicked.connect(lambda: self._switch_tab(0))
        self.btn_history.clicked.connect(lambda: self._switch_tab(1))
        self.btn_settings.clicked.connect(lambda: self._switch_tab(2))

        main_layout.addLayout(sidebar, 1)
        main_layout.addWidget(self.tabs, 6)

    def _switch_tab(self, index: int):
        self.tabs.setCurrentIndex(index)
        self.btn_home.setChecked(index == 0)
        self.btn_history.setChecked(index == 1)
        self.btn_settings.setChecked(index == 2)

    def _build_home_tab(self):
        layout = QVBoxLayout()
        self.tab_home.setLayout(layout)

        url_label = QLabel("Enter Video URL:")
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("https://youtube.com/...")
        layout.addWidget(url_label)
        layout.addWidget(self.input_url)

        format_label = QLabel("Select Format:")
        self.combo_format = QComboBox()
        self.combo_format.addItems([
            "Best Video + Audio (mp4/mkv)", "Audio-only (mp3)", "720p mp4", "1080p mp4", "MKV"
        ])
        layout.addWidget(format_label)
        layout.addWidget(self.combo_format)

        btn_layout = QHBoxLayout()
        self.btn_browse = QPushButton("Select Download Folder")
        self.label_folder = QLabel(str(self.download_path))
        self.btn_download = QPushButton("Download")

        btn_layout.addWidget(self.btn_browse)
        btn_layout.addWidget(self.label_folder)
        btn_layout.addWidget(self.btn_download)
        layout.addLayout(btn_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        control_layout = QHBoxLayout()
        self.btn_pause = QPushButton("Pause")
        self.btn_resume = QPushButton("Resume")
        self.btn_cancel = QPushButton("Cancel")
        control_layout.addWidget(self.btn_pause)
        control_layout.addWidget(self.btn_resume)
        control_layout.addWidget(self.btn_cancel)
        layout.addLayout(control_layout)

        log_label = QLabel("Log:")
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        layout.addWidget(log_label)
        layout.addWidget(self.text_log)

        self.btn_browse.clicked.connect(self.select_download_folder)
        self.btn_download.clicked.connect(self.handle_download)
        self.btn_pause.clicked.connect(self.downloader.pause_download)
        self.btn_resume.clicked.connect(self.downloader.resume_download)
        self.btn_cancel.clicked.connect(self.downloader.cancel_download)

    def _build_history_tab(self):
        layout = QVBoxLayout()
        self.tab_history.setLayout(layout)

        self.list_history = QListWidget()
        layout.addWidget(self.list_history)

        self.btn_open_file = QPushButton("Open Selected File")
        layout.addWidget(self.btn_open_file)
        self.btn_open_file.clicked.connect(self.open_selected_history_file)

        self.btn_delete_history = QPushButton("Delete History Entry & File")
        layout.addWidget(self.btn_delete_history)
        self.btn_delete_history.clicked.connect(self.delete_selected_history_entry)

        self.list_history.itemDoubleClicked.connect(self.open_selected_history_file)

    def _build_settings_tab(self):
        layout = QVBoxLayout()
        self.tab_settings.setLayout(layout)

        self.checkbox_dark_mode = QCheckBox("Dark Mode")
        self.checkbox_dark_mode.setChecked(self.dark_mode)
        layout.addWidget(self.checkbox_dark_mode)
        self.checkbox_dark_mode.stateChanged.connect(self.toggle_dark_mode)

        path_layout = QHBoxLayout()
        self.input_default_path = QLineEdit()
        self.input_default_path.setText(str(self.download_path))
        path_layout.addWidget(self.input_default_path)
        self.btn_change_path = QPushButton("Change Path")
        path_layout.addWidget(self.btn_change_path)
        layout.addLayout(path_layout)
        self.btn_change_path.clicked.connect(self.select_default_download_path)

        self.btn_save_settings = QPushButton("Save Settings")
        layout.addWidget(self.btn_save_settings)
        self.btn_save_settings.clicked.connect(self.save_settings)

    def select_download_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", str(self.download_path))
        if folder:
            self.download_path = Path(folder)
            self.label_folder.setText(str(folder))

    def select_default_download_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Default Download Folder", str(self.download_path))
        if folder:
            self.input_default_path.setText(folder)

    def toggle_dark_mode(self, state):
        self.apply_theme(state == Qt.CheckState.Checked)

    def apply_theme(self, dark_mode: bool):
        self.dark_mode = dark_mode
        if dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #121212;
                    color: #e0e0e0;
                }
                QLineEdit, QTextEdit {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                }
                QPushButton {
                    background-color: #303030;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QProgressBar {
                    border: 1px solid #555555;
                    text-align: center;
                    background: #1e1e1e;
                    color: #e0e0e0;
                }
                QProgressBar::chunk {
                    background-color: #3a8ee6;
                }
                QListWidget {
                    background: #1e1e1e;
                    color: #e0e0e0;
                }
            """)
        else:
            self.setStyleSheet("")

    def save_settings(self):
        self.settings.set("dark_mode", self.checkbox_dark_mode.isChecked())
        self.settings.set("download_path", self.input_default_path.text())
        self.settings.save()
        QMessageBox.information(self, "Settings", "Settings saved successfully.\nPlease restart app to apply some changes.")

    def handle_download(self):
        url = self.input_url.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a video URL.")
            return

        format_choice = self.combo_format.currentText()
        if format_choice == "Audio-only (mp3)":
            format_code = "bestaudio"
            postprocessor = "mp3"
        elif format_choice == "720p mp4":
            format_code = "bestvideo[height<=720]+bestaudio/best[height<=720]"
            postprocessor = None
        elif format_choice == "1080p mp4":
            format_code = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
            postprocessor = None
        elif format_choice == "MKV":
            format_code = "bestvideo+bestaudio/best"
            postprocessor = None
        else:
            format_code = "bestvideo+bestaudio/best"
            postprocessor = None

        self.progress_bar.setValue(0)
        self.text_log.clear()
        self.downloader.start_download(
            url=url,
            download_path=self.download_path,
            format_code=format_code,
            postprocessor=postprocessor,
        )

    def on_progress_update(self, progress: float, speed_str: str = "", eta_str: str = ""):
        self.progress_bar.setValue(int(progress))
        self.text_log.append(f"Progress: {progress:.2f}% Speed: {speed_str} ETA: {eta_str}")

    def on_download_finished(self, title: str, filepath: str, url: str):
        self.text_log.append(f"Download finished: {title}")
        self.progress_bar.setValue(100)
        self.history_db.add_entry(title=title, filepath=filepath, url=url)
        self.load_history()

    def on_download_error(self, error_msg: str):
        self.text_log.append(f"Error: {error_msg}")
        QMessageBox.critical(self, "Download Error", error_msg)

    def load_history(self):
        self.list_history.clear()
        entries = self.history_db.get_all_entries()
        for entry in entries:
            item = QListWidgetItem(f"{entry['title']}  [{entry['date']}]")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.list_history.addItem(item)

    def open_selected_history_file(self):
        selected_items = self.list_history.selectedItems()
        if not selected_items:
            return
        entry = selected_items[0].data(Qt.ItemDataRole.UserRole)
        filepath = entry['filepath']
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "File Not Found", "The downloaded file is missing.")
            return
        if os.name == "nt":
            os.startfile(filepath)
        else:
            os.system(f'xdg-open "{filepath}"')

    def delete_selected_history_entry(self):
        selected_items = self.list_history.selectedItems()
        if not selected_items:
            return
        entry = selected_items[0].data(Qt.ItemDataRole.UserRole)
        filepath = entry['filepath']
        reply = QMessageBox.question(self, "Delete Confirmation",
                                     f"Delete history and file:\n{entry['title']}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.history_db.delete_entry(entry['id'])
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete file:\n{str(e)}")
            self.load_history()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
