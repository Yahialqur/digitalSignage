import sys
import requests
import os
import threading
import time
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap
from flask import Flask, jsonify

SERVER_URL = ""  # Add admin server IP
LOCAL_SLIDES_FOLDER = "slides"
REFRESH_INTERVAL = 10  # Time in seconds between slide changes

app = Flask(__name__)

class BranchDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.slides = []
        self.current_index = 0
        self.running = True
        self.download_slides()
        threading.Thread(target=self.slideshow, daemon=True).start()

    def initUI(self):
        layout = QVBoxLayout()
        self.label = QLabel("Fetching slides...", self)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setWindowTitle("Digital Signage Display")
        self.setGeometry(300, 300, 1280, 720)

    def download_slides(self):
        """Fetch latest slides from the server"""
        os.makedirs(LOCAL_SLIDES_FOLDER, exist_ok=True)

        try:
            response = requests.get(f"{SERVER_URL}/slides")
            if response.status_code == 200:
                slide_list = response.json().get("slides", [])
                self.slides = []

                for slide in slide_list:
                    slide_path = os.path.join(LOCAL_SLIDES_FOLDER, slide)
                    response = requests.get(f"{SERVER_URL}/slides/{slide}")

                    if response.status_code == 200:
                        with open(slide_path, "wb") as f:
                            f.write(response.content)
                        self.slides.append(slide_path)

        except requests.exceptions.RequestException:
            print("Failed to fetch slides from server")

    def slideshow(self):
        """Cycle through slides"""
        while self.running:
            if self.slides:
                slide_path = self.slides[self.current_index]
                self.display_slide(slide_path)
                self.current_index = (self.current_index + 1) % len(self.slides)

            time.sleep(REFRESH_INTERVAL)

    def display_slide(self, slide_path):
        """Display an image slide"""
        pixmap = QPixmap(slide_path)
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

@app.route('/reload')
def reload_slides():
    """Endpoint to trigger slide reload"""
    display_window.download_slides()
    return jsonify({"message": "Slides reloaded successfully"}), 200

if __name__ == "__main__":
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5001, debug=False), daemon=True)
    flask_thread.start()

    app = QApplication(sys.argv)
    display_window = BranchDisplay()
    display_window.show()
    sys.exit(app.exec())
