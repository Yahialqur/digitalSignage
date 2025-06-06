import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog

# Server machine Ip
SERVER_URL = ""  #Add server ip and port here

class AdminApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Upload a PowerPoint file to start")
        layout.addWidget(self.status_label)

        upload_btn = QPushButton("Upload PowerPoint")
        upload_btn.clicked.connect(self.upload_ppt)
        layout.addWidget(upload_btn)

        reload_btn = QPushButton("Reload Slides at Branches")
        reload_btn.clicked.connect(self.reload_slides)
        layout.addWidget(reload_btn)

        self.setLayout(layout)
        self.setWindowTitle("Control")
        self.setGeometry(300, 300, 400, 200)

    def upload_ppt(self):
        """
        Opens a file chooser for a .pptx, then sends it to the server's /upload endpoint.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PowerPoint File", "", "PowerPoint Files (*.pptx)")
        if file_path:
            self.status_label.setText("Uploading...")
            try:
                with open(file_path, 'rb') as f:
                    response = requests.post(f"{SERVER_URL}/upload", files={'file': f})
            except requests.exceptions.RequestException as e:
                self.status_label.setText(f"Upload failed: {e}")
                return
            
            if response.status_code == 200:
                self.status_label.setText("Upload successful. Slides processed.")
            else:
                self.status_label.setText("Upload failed. Try again.")

    def reload_slides(self):
        """
        Calls the server's /reload to force a refresh on branch displays.
        """
        try:
            response = requests.get(f"{SERVER_URL}/reload")
        except requests.exceptions.RequestException as e:
            self.status_label.setText(f"Failed to reload slides: {e}")
            return

        if response.status_code == 200:
            self.status_label.setText("Slides reloaded at branches.")
        else:
            self.status_label.setText("Failed to reload slides.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    admin_window = AdminApp()
    admin_window.show()
    sys.exit(app.exec())
