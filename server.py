import os
import shutil
import subprocess
import threading

import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
SLIDES_FOLDER = "static/slides"

# List of branch client base URLs
BRANCH_CLIENTS = ["", ""]  #Add branch client ips and ports here

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SLIDES_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_pptx():
    """
    Endpoint to receive a PPTX file via multipart form-data.
    Converts it to PDF, then to multiple PNG pages, and notifies branches to reload.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    pptx_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pptx_path)

    convert_pptx_to_images(pptx_path)
    notify_branches()
    
    return jsonify({"message": "Slides uploaded and processed successfully"}), 200

def convert_pptx_to_images(pptx_path):
    """
    Two-step approach:
    1) Convert PPTX -> PDF (via LibreOffice)
    2) Convert PDF -> multiple PNG pages (via pdftoppm from Poppler)
    """
    # 1) Clear old slides
    if os.path.exists(SLIDES_FOLDER):
        shutil.rmtree(SLIDES_FOLDER)
    os.makedirs(SLIDES_FOLDER, exist_ok=True)

    # 2) Convert PPTX to PDF in SLIDES_FOLDER
    print("Converting PPTX to PDF...")
    pdf_command = [
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", SLIDES_FOLDER,
        pptx_path
    ]
    pdf_result = subprocess.run(pdf_command, capture_output=True, text=True)
    print("LibreOffice PDF stdout:", pdf_result.stdout)
    print("LibreOffice PDF stderr:", pdf_result.stderr)
    print("LibreOffice PDF returncode:", pdf_result.returncode)
    if pdf_result.returncode != 0:
        raise RuntimeError("LibreOffice failed to convert PPTX to PDF.")

    base_name = os.path.splitext(os.path.basename(pptx_path))[0]
    pdf_path = os.path.join(SLIDES_FOLDER, base_name + ".pdf")

    if not os.path.exists(pdf_path):
        # If the name is different or if something went wrong, check the directory for a .pdf
        possible_pdfs = [f for f in os.listdir(SLIDES_FOLDER) if f.lower().endswith(".pdf")]
        if possible_pdfs:
            pdf_path = os.path.join(SLIDES_FOLDER, possible_pdfs[0])
        else:
            raise FileNotFoundError("Expected PDF not found after LibreOffice conversion.")

    # 3) Convert PDF -> multiple PNGs with pdftoppm
    #    This will create slides named like slide-1.png, slide-2.png, etc.
    print("Converting PDF to multiple PNG pages...")
    png_command = [
        "pdftoppm",
        pdf_path,
        os.path.join(SLIDES_FOLDER, "slide"), 
        "-png"
    ]
    png_result = subprocess.run(png_command, capture_output=True, text=True)
    print("pdftoppm stdout:", png_result.stdout)
    print("pdftoppm stderr:", png_result.stderr)
    print("pdftoppm returncode:", png_result.returncode)
    if png_result.returncode != 0:
        raise RuntimeError("pdftoppm failed to convert PDF to PNG pages.")

    # 4) Remove the PDF, now that we have PNG slides
    try:
        os.remove(pdf_path)
    except OSError:
        pass

    # 5) Print final set of files in SLIDES_FOLDER
    generated_files = os.listdir(SLIDES_FOLDER)
    print("Files in slides folder after PDF->PNG:", generated_files)

@app.route('/slides')
def get_slides():
    """
    Returns a JSON list of all PNG files in the slides folder.
    Example: { "slides": ["slide-1.png", "slide-2.png", ...] }
    """
    slides = sorted(os.listdir(SLIDES_FOLDER))
    return jsonify({"slides": slides})

@app.route('/slides/<filename>')
def serve_slide(filename):
    """
    Serves an individual slide (PNG file) from the slides folder.
    """
    return send_from_directory(SLIDES_FOLDER, filename)

@app.route('/reload')
def reload_branches():
    """
    Manually trigger branch reload via GET request.
    """
    notify_branches()
    return jsonify({"message": "Branches notified to reload"}), 200

def notify_branches():
    """
    In a separate thread, sends a GET /reload request to each branch.
    """
    def notify():
        for branch_url in BRANCH_CLIENTS:
            try:
                requests.get(f"{branch_url}/reload")
            except requests.exceptions.RequestException:
                print(f"Failed to notify {branch_url}")
    
    threading.Thread(target=notify).start()

if __name__ == '__main__':
    # Run the server on 0.0.0.0 port 5001
    app.run(host='0.0.0.0', port=5001, debug=True)
