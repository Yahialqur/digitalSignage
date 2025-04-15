import sys
import os
import shutil
import threading
import requests
from flask import Flask, jsonify
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer

# Server Ip
SERVER_URL = ""   #Add server ip and port here

# Local folder to store downloaded slide PNGs
LOCAL_SLIDES_FOLDER = "slides"

# Number of seconds each slide is shown
REFRESH_INTERVAL = 10

flask_app = Flask(__name__)

class BranchDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        self.slides = []
        self.current_index = 0
        
        # Download initial slides
        self.download_slides()
        
        # Use a QTimer to cycle slides
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next_slide)
        self.timer.start(REFRESH_INTERVAL * 1000)

    def initUI(self):
        layout = QVBoxLayout()
        self.label = QLabel("Fetching slides...", self)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setWindowTitle("Digital Signage Display")
        self.setGeometry(300, 300, 1280, 720)

    def download_slides(self):
        """
        Fetches the latest slide filenames from the server, downloads each PNG,
        and stores them in LOCAL_SLIDES_FOLDER. Old slides are cleared first.
        """
        # Clear slides folder
        if os.path.exists(LOCAL_SLIDES_FOLDER):
            shutil.rmtree(LOCAL_SLIDES_FOLDER)
        os.makedirs(LOCAL_SLIDES_FOLDER, exist_ok=True)

        self.slides = []
        try:
            # Get list of slides from server
            response = requests.get(f"{SERVER_URL}/slides")
            response.raise_for_status()

            slide_list = response.json().get("slides", [])

            # Download each slide
            for slide_name in slide_list:
                slide_url = f"{SERVER_URL}/slides/{slide_name}"
                slide_path = os.path.join(LOCAL_SLIDES_FOLDER, slide_name)

                r = requests.get(slide_url)
                r.raise_for_status()

                with open(slide_path, "wb") as f:
                    f.write(r.content)

                self.slides.append(slide_path)

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch slides from server: {e}")

        # Reset slideshow index to start from beginning
        self.current_index = 0
        
        # If there's at least one slide, display it immediately
        if self.slides:
            self.display_slide(self.slides[0])
        else:
            self.label.setText("No slides found on server.")

    def show_next_slide(self):
        """
        Called by the QTimer every REFRESH_INTERVAL seconds.
        Cycles to the next slide and updates the QLabel.
        """
        if not self.slides:
            return  # No slides to show

        self.current_index = (self.current_index + 1) % len(self.slides)
        slide_path = self.slides[self.current_index]
        self.display_slide(slide_path)

    def display_slide(self, slide_path):
        """
        Load slide PNG into a QPixmap and display it in the QLabel.
        """
        pixmap = QPixmap(slide_path)
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

@flask_app.route('/reload')
def reload_slides():
    """
    Flask endpoint called by the server's notify_branches() thread.
    This triggers a re-download of the slides without stopping the app.
    """
    display_window.download_slides()
    return jsonify({"message": "Slides reloaded successfully"}), 200

if __name__ == "__main__":
    # 1. Start the Flask server in a background thread, so we can respond to /reload.
    flask_thread = threading.Thread(
        target=lambda: flask_app.run(host="0.0.0.0", port=5002, debug=False),
        daemon=True
    )
    flask_thread.start()

    # 2. Start the PyQt app for slideshow.
    qt_app = QApplication(sys.argv)
    display_window = BranchDisplay()
    display_window.show()
    sys.exit(qt_app.exec())
