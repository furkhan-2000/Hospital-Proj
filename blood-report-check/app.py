import os
import uuid
import logging
import traceback
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import pytesseract
import pdfplumber
import pydicom
import cv2
import numpy as np
from extractor import extract_entities
from recommendation import analyze_and_recommend

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'dcm'}

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

logger = logging.getLogger('BloodAnalysis')
logger.setLevel(logging.INFO)
LOG_FILE = os.path.join(UPLOAD_DIR, 'blood_analysis.log')  
handler = RotatingFileHandler(LOG_FILE, maxBytes=int(1e6), backupCount=3)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


@app.errorhandler(400)
def bad_request(error):
    logger.error(f"400 Error: {error}")
    return jsonify({'error': 'Bad request', 'details': str(error)}), 400

@app.errorhandler(500)
def server_error(error):
    logger.error(f"500 Error: {error}")
    return jsonify({'error': 'Server error', 'details': str(error)}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def enhance_image(image):
    try:
        arr = np.array(image)
        gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 3)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return Image.fromarray(thresh)
    except Exception as e:
        logger.error(f'Image enhancement failed: {e}')
        return image

def extract_text(file_path, extension):
    try:
        if extension in {'.png', '.jpg', '.jpeg'}:
            img = Image.open(file_path)
            img = enhance_image(img)
            return pytesseract.image_to_string(img, config='--psm 11')
        elif extension == '.pdf':
            text = ''
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ''
                    if not page_text:
                        page_text = pytesseract.image_to_string(page.to_image().original, config='--psm 11')
                    text += page_text
            return text
        elif extension == '.dcm':
            ds = pydicom.dcmread(file_path)
            return f"{ds.get('StudyDescription', '')} {ds.get('PatientComments', '')}"
    except Exception as e:
        logger.error(f'Text extraction failed: {e}')
    return ''

def analyze_content(file_path, gender="male"):
    try:
        extension = os.path.splitext(file_path)[1].lower()
        raw_text = extract_text(file_path, extension)
        if not raw_text:
            return {'error': 'No content'}, 400

        results = extract_entities(raw_text)
        if not results:
            return {'error': 'No results'}, 400

        recommendations = analyze_and_recommend(results, gender=gender)
        return {
            'recommendations': recommendations
        }, 200
    except Exception:
        logger.error(f'Analyze failed: {traceback.format_exc()}')
        return {'error': 'Analyze error'}, 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_file():
    cid = str(uuid.uuid4())
    logger.info(f'[{cid}] Start analysis')

    if 'file' not in request.files:
        logger.warning(f'[{cid}] No file part in request')
        return jsonify({'error': 'No file'}), 400

    file = request.files['file']
    if not file.filename or not allowed_file(file.filename):
        logger.warning(f'[{cid}] Invalid file')
        return jsonify({'error': 'Invalid file'}), 400

    extension = os.path.splitext(file.filename)[1]
    temp_path = os.path.join(UPLOAD_DIR, f"{cid}{extension}")
    file.save(temp_path)

    gender = request.form.get('gender', 'male').lower()
    data, status = analyze_content(temp_path, gender)
    os.remove(temp_path)

    if status == 200:
        logger.info(f'[{cid}] Analysis successful')
        return jsonify({'status': 'ok', 'cid': cid, 'data': data}), 200

    logger.warning(f'[{cid}] Analysis failed with status {status}')
    return jsonify(data), status

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
