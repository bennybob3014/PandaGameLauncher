import sys
import os
import json
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QLabel, QDialog, QLineEdit, QMessageBox, QHBoxLayout
)
from PyQt6.QtGui import QPalette, QBrush, QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize

LIBRARY_FILE = "game_library.json"
BACKGROUND_IMAGE = "PandaGameLauncher.png"
DEFAULT_ICON = "default_icon.png"  # Make sure you have a default icon here

class GameSettingsDialog(QDialog):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Game")
        self.game = game
        self.setLayout(QVBoxLayout())

        self.name_input = QLineEdit(game["name"])
        self.path_input = QLineEdit(game["path"])
        self.icon_input = QLineEdit(game.get("icon", ""))

        self.layout().addWidget(QLabel("Game Name:"))
        self.layout().addWidget(self.name_input)
        self.layout().addWidget(QLabel("Executable Path:"))
        self.layout().addWidget(self.path_input)
        self.layout().addWidget(QLabel("Icon Path:"))
        self.layout().addWidget(self.icon_input)

        browse_icon_btn = QPushButton("Browse for Icon")
        browse_icon_btn.clicked.connect(self.pick_icon)
        self.layout().addWidget(browse_icon_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        self.layout().addWidget(save_btn)

    def pick_icon(self):
        icon_path, _ = QFileDialog.getOpenFileName(self, "Choose Icon", filter="Images (*.png *.jpg *.ico)")
        if icon_path:
            self.icon_input.setText(icon_path)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "path": self.path_input.text(),
            "icon": self.icon_input.text()
        }

class PandaLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panda Game Launcher")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.resize(900, 650)

        # Main vertical layout container
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.game_list_widget = QListWidget()
        self.game_list_widget.setIconSize(QSize(48, 48))

        # Container widget to hold list and watermark
        container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_widget.setLayout(container_layout)

        container_layout.addWidget(self.game_list_widget)

        # Watermark label at bottom right
        watermark = QLabel("© 2025 Benthepanda. All rights reserved.")
        watermark.setStyleSheet("color: #888888; font-size: 10px;")
        watermark.setAlignment(Qt.AlignmentFlag.AlignRight)
        container_layout.addWidget(watermark)

        main_layout.addWidget(container_widget)

        self.add_button = QPushButton("➕ Add Game")
        self.add_button.clicked.connect(self.add_game)
        main_layout.addWidget(self.add_button)

        self.launch_button = QPushButton("🚀 Launch Game")
        self.launch_button.clicked.connect(self.launch_game)
        main_layout.addWidget(self.launch_button)

        self.settings_button = QPushButton("⚙️ Edit Selected Game")
        self.settings_button.clicked.connect(self.edit_game)
        main_layout.addWidget(self.settings_button)

        self.games = []
        self.load_library()
        self.refresh_list()
        self.set_panda_style()
        self.showFullScreen()

    def set_panda_style(self):
        if os.path.exists(BACKGROUND_IMAGE):
            palette = QPalette()
            pixmap = QPixmap(BACKGROUND_IMAGE).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)
            palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
        else:
            self.setStyleSheet("""
                background-color: #121212;
                color: #e0e0e0;
            """)

        button_style = """
            background-color: #333333;
            color: #e0e0e0;
            padding: 10px;
            border-radius: 10px;
        """
        self.add_button.setStyleSheet(button_style)
        self.launch_button.setStyleSheet(button_style)
        self.settings_button.setStyleSheet(button_style)

        self.game_list_widget.setStyleSheet("""
            background-color: #222222;
            color: #e0e0e0;
            selection-background-color: #555555;
        """)

    def load_library(self):
        if os.path.exists(LIBRARY_FILE):
            with open(LIBRARY_FILE, "r") as f:
                self.games = json.load(f)
        else:
            self.games = []

    def save_library(self):
        with open(LIBRARY_FILE, "w") as f:
            json.dump(self.games, f, indent=2)

    def refresh_list(self):
        self.game_list_widget.clear()
        for game in self.games:
            icon_path = game.get("icon") or DEFAULT_ICON
            icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
            item = QListWidgetItem(icon, game["name"])
            self.game_list_widget.addItem(item)

    def add_game(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Game Executable", filter="Executables (*.exe)")
        if path:
            icon_path, _ = QFileDialog.getOpenFileName(self, "Pick Game Icon (optional)", filter="Images (*.png *.jpg *.ico)")
            name = os.path.basename(path)
            self.games.append({
                "name": name,
                "path": path,
                "icon": icon_path if icon_path else DEFAULT_ICON
            })
            self.save_library()
            self.refresh_list()

    def edit_game(self):
        index = self.game_list_widget.currentRow()
        if index < 0:
            QMessageBox.information(self, "No selection", "Pick a game first!")
            return
        dialog = GameSettingsDialog(self.games[index], self)
        if dialog.exec():
            self.games[index] = dialog.get_data()
            self.save_library()
            self.refresh_list()

    def launch_game(self):
        index = self.game_list_widget.currentRow()
        if index < 0:
            QMessageBox.information(self, "No selection", "Pick a game to launch!")
            return
        game = self.games[index]
        try:
            subprocess.Popen([game["path"]], cwd=os.path.dirname(game["path"]))
            self.close()  # Close launcher after launching game
        except Exception as e:
            QMessageBox.critical(self, "Launch Failed", f"Error launching game:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = PandaLauncher()
    launcher.show()
    sys.exit(app.exec())
