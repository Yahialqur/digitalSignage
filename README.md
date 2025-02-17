# Digital Signage Software

## Overview
This is a project I worked on to help a local mid-sized business. With over 20 branches they needed a software to manage their digital signage. 
This digital signage software enables centralized management of PowerPoint slides that are displayed on screens across multiple branch locations. The system includes an admin application for uploading slides, a server for processing and distributing them, and a client application at each branch to display the slides.

## Features
- **Admin Application**: Allows uploading PowerPoint presentations and triggering slide reloads at all branches.
- **Server**: Handles PPTX file uploads, converts them to images, and notifies branch clients to update.
- **Branch Client Application**: Downloads and displays slides in a continuous loop.

## Architecture
- **Admin App (`admin_app.py`)**: GUI application for uploading slides and reloading branches.
- **Server (`server.py`)**: Flask-based backend that processes PowerPoint files and notifies branch clients.
- **Branch Client (`branch_app.py`)**: PyQt-based application that downloads and displays slides.

## Installation
### Prerequisites
- **Python 3**
- **Flask**
- **PyQt6**
- **LibreOffice** (for PPTX to PDF conversion)
- **Poppler** (for PDF to PNG conversion)

### Installing Dependencies
Run the following command to install required dependencies from the `requirements.txt` file:
```sh
pip install -r requirements.txt
```

For LibreOffice and Poppler:
Run the following command to install required dependencies:
```sh
pip install flask pyqt6 requests
```

For LibreOffice and Poppler:
- **Ubuntu/Debian**:
  ```sh
  sudo apt install libreoffice poppler-utils
  ```
- **MacOS (using Homebrew)**:
  ```sh
  brew install libreoffice poppler
  ```
- **Windows**:
  - Install LibreOffice from [official website](https://www.libreoffice.org/)
  - Install Poppler for Windows and add `pdftoppm.exe` to the system PATH.

## Usage
### Running the Server
```sh
python server.py
```
The server will run on `http://0.0.0.0:5001` and listen for admin and branch requests.

### Running the Admin App
```sh
python admin_app.py
```
The admin app provides a GUI for uploading PowerPoint files and reloading slides at all branches.

### Running the Branch Client App
```sh
python branch_app.py
```
Each branch machine runs the client app, which fetches and displays the latest slides.

## How It Works
1. **Upload PPTX File**: The admin uploads a PowerPoint file via the admin app.
2. **Processing on Server**:
   - Converts PPTX → PDF using LibreOffice.
   - Converts PDF → PNG slides using Poppler.
   - Stores PNG slides in the `static/slides/` directory.
   - Notifies branch clients to reload.
3. **Branch Clients Fetch Slides**:
   - Download the latest slides from the server.
   - Display them in a continuous loop.
   - Refresh automatically when notified by the server.

## API Endpoints
| Endpoint        | Method | Description |
|---------------|--------|-------------|
| `/upload`     | POST   | Uploads a PowerPoint file for conversion |
| `/slides`     | GET    | Retrieves a list of available slide images |
| `/slides/<filename>` | GET | Serves an individual slide image |
| `/reload`     | GET    | Notifies branch clients to refresh slides |

## Configuration
- Modify `SERVER_URL` in `branch_app.py` and `admin_app.py` to match the server's IP address.
- Modify `BRANCH_CLIENTS` in `server.py` to include all branch client IP addresses.

## Troubleshooting
- **LibreOffice conversion issues**: Ensure `libreoffice` is installed and accessible from the command line.
- **Poppler conversion issues**: Ensure `pdftoppm` is installed and added to system PATH.
- **Branch clients not updating**: Check that the branch app is running and can reach the server.

