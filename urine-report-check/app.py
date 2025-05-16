import os
import re
import uuid
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, send_from_directory, abort, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance
import pytesseract
import pdfplumber
import pydicom

# Configuration
UPLOAD_DIR = 'uploads'
PORT = 5001
LOG_FILE = 'app.log'
ALLOWED_EXT = {'.pdf', '.jpeg', '.jpg', '.png', '.dcm'}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Flask app
app = Flask(
    __name__,
    static_folder=None,
    template_folder='templates'
)
CORS(app)

# Logging setup with rotation
logger = logging.getLogger('flask_app')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(cid)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.before_request
def before_request():
    cid = request.headers.get('X-Correlation-Id', str(uuid.uuid4()))
    request.cid = cid
    request.logger = logging.LoggerAdapter(logger, {'cid': cid})
    request.logger.info(f"Incoming {request.method} {request.path} from {request.remote_addr}")

# ---------------------------
# Helper Functions: File Extraction & Preprocessing
# ---------------------------
def preprocess_image(path):
    try:
        img = Image.open(path).convert('L')
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        img = img.resize((img.width * 2, img.height * 2))
        return img
    except Exception as e:
        logger.error(f"Error in preprocess_image: {e}")
        return None

def extract_text(path, ext):
    text = ""
    try:
        if ext in {'.jpeg', '.jpg', '.png'}:
            img = preprocess_image(path)
            if img:
                text = pytesseract.image_to_string(img)
        elif ext == '.pdf':
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        elif ext == '.dcm':
            ds = pydicom.dcmread(path)
            text = "\n".join(f"{e.keyword}: {e.value}" for e in ds if hasattr(e, 'keyword'))
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
    return text

# ---------------------------
# Advanced Urine Test Analysis Modules
# ---------------------------
def analyze_microbiology(bacterial_load, microbial_composition, detected_pathogens, resistance_genes, symptoms):
    results = []
    BA_THRESHOLD = 1e5
    try:
        if bacterial_load >= BA_THRESHOLD:
            results.append("High bacterial load indicates potential infection.")
    except Exception as e:
        results.append("Bacterial load value error.")
        logger.error(f"Error checking bacterial load: {e}")

    beneficial_pct = microbial_composition.get("lactobacillus gasseri", 0)
    if beneficial_pct < 70:
        results.append("Low proportion of beneficial bacteria (Lactobacillus spp.) suggests imbalance.")

    common_pathogens = {"escherichia coli", "klebsiella pneumoniae", "staphylococcus aureus"}
    common_detected = set([p.lower() for p in detected_pathogens]).intersection(common_pathogens)
    if common_detected:
        results.append("Detected common pathogens: " + ", ".join(common_detected))
    if resistance_genes:
        results.append("Resistance genes detected; correlate with clinical findings.")
    if symptoms:
        results.append("Patient is symptomatic, warranting further evaluation.")

    if not results:
        return "Microbiology (Culture) Analysis: Normal."
    else:
        return "Microbiology (Culture) Analysis: " + " | ".join(results)

def analyze_chemistry(chem_data):
    results = []
    try:
        if "pH" in chem_data:
            pH = chem_data["pH"]
            if pH < 4.6 or pH > 8.0:
                results.append(f"pH ({pH}) is out of the normal range (4.6–8.0).")
        if "color" in chem_data:
            color = chem_data["color"].lower()
            if any(x in color for x in ["red", "brown", "cloudy"]):
                results.append(f"Color '{chem_data['color']}' is abnormal.")
        if "clarity" in chem_data:
            clarity = chem_data["clarity"].lower()
            if clarity not in ["clear", "normal"]:
                results.append(f"Clarity '{chem_data['clarity']}' is abnormal.")
        if "odor" in chem_data:
            odor = chem_data["odor"].lower()
            if "fruity" in odor or "foul" in odor:
                results.append(f"Odor '{chem_data['odor']}' is abnormal.")
        if "specific_gravity" in chem_data:
            sg = chem_data["specific_gravity"]
            if sg < 1.005 or sg > 1.030:
                results.append(f"Specific Gravity ({sg}) is out of range (1.005–1.030).")
        if "protein" in chem_data:
            protein = chem_data["protein"]
            if protein > 15:
                results.append(f"Protein level ({protein} mg/dL) is elevated (normal <15 mg/dL).")
        for param in ["glucose", "ketones", "blood", "nitrites", "leukocyte_esterase"]:
            if param in chem_data:
                value = chem_data[param].lower()
                if value != "negative":
                    results.append(f"{param.capitalize()} is abnormal: {chem_data[param]}.")
        if "microalbumin" in chem_data:
            microalbumin = chem_data["microalbumin"]
            if microalbumin > 30:
                results.append(f"Microalbumin ({microalbumin} mg/day) is elevated (normal <30 mg/day).")
    except Exception as e:
        results.append("Chemical data error.")
        logger.error(f"Error in chemistry analysis: {e}")

    if not results:
        return "Chemical Analysis (Dipstick): All parameters are normal."
    else:
        return "Chemical Analysis (Dipstick): " + " | ".join(results)

def analyze_microscopic(microscopic_data):
    results = []
    try:
        if "rbc" in microscopic_data:
            if microscopic_data["rbc"] > 3:
                results.append(f"RBC count ({microscopic_data['rbc']}/HPF) is elevated (normal 0-3/HPF).")
        if "wbc" in microscopic_data:
            if microscopic_data["wbc"] >= 5:
                results.append(f"WBC count ({microscopic_data['wbc']}/HPF) is high (normal <5/HPF).")
        if "casts" in microscopic_data:
            casts = microscopic_data["casts"].lower()
            if casts not in ["none", "negative", "rare", ""]:
                results.append(f"Casts reported as '{microscopic_data['casts']}' may be abnormal.")
        if "crystals" in microscopic_data:
            crystals = microscopic_data["crystals"].lower()
            if crystals not in ["none", "negative", "rare", ""]:
                results.append(f"Crystals reported as '{microscopic_data['crystals']}' may indicate pathology.")
        if "epithelial_cells" in microscopic_data:
            if microscopic_data["epithelial_cells"] > 5:
                results.append(f"Epithelial cells count ({microscopic_data['epithelial_cells']}/HPF) is high (normal <5/HPF).")
    except Exception as e:
        results.append("Microscopic data error.")
        logger.error(f"Error in microscopic analysis: {e}")

    if not results:
        return "Microscopic Analysis: Normal findings."
    else:
        return "Microscopic Analysis: " + " | ".join(results)

def analyze_24hour_volume(volume):
    try:
        if volume is None:
            return "No 24-hour urine volume provided."
        if volume < 600:
            return f"24-Hour Urine Volume ({volume} mL) is low (oliguria)."
        elif volume > 3600:
            return f"24-Hour Urine Volume ({volume} mL) is high (polyuria)."
        else:
            return f"24-Hour Urine Volume ({volume} mL) is within the normal range."
    except Exception as e:
        logger.error(f"Error in volume analysis: {e}")
        return "24-Hour Volume analysis error."

def analyze_rapid_urine(rapid_data):
    issues = []
    try:
        for param in ["nitrites", "leukocyte_esterase", "glucose", "protein", "blood"]:
            if param in rapid_data:
                value = rapid_data[param].lower()
                if value != "negative":
                    issues.append(f"{param.capitalize()} abnormal: {rapid_data[param]}")
    except Exception as e:
        logger.error(f"Error in rapid urine analysis: {e}")
        issues.append("Rapid urine data error.")
    if issues:
        return "Rapid Urine Test: Abnormal - " + " | ".join(issues)
    else:
        return "Rapid Urine Test: Normal."

def analyze_pregnancy_test(pregnancy_data):
    try:
        if "result" in pregnancy_data:
            result = pregnancy_data["result"].lower()
            if result == "positive":
                return "Pregnancy Test: Positive."
            elif result == "negative":
                return "Pregnancy Test: Negative."
            else:
                return f"Pregnancy Test: Unclear result ({pregnancy_data['result']})."
        if "hcg" in pregnancy_data:
            try:
                hcg_value = float(pregnancy_data["hcg"])
            except ValueError:
                return "Pregnancy Test: Invalid hCG value."
            if hcg_value >= 20:
                return f"Pregnancy Test: Positive (hCG: {hcg_value} mIU/mL)."
            else:
                return f"Pregnancy Test: Negative (hCG: {hcg_value} mIU/mL)."
    except Exception as e:
        logger.error(f"Error in pregnancy test analysis: {e}")
        return "Pregnancy Test analysis error."
    return "Pregnancy Test: Insufficient data."

def analyze_urine_test(data):
    test_type = data.get("test_type", "full").lower()
    sections = []
    try:
        if test_type == "rapid":
            sections.append(analyze_rapid_urine(data.get("rapid_data", {})))
        elif test_type == "complete":
            sections.append(analyze_chemistry(data.get("chem_data", {})))
            if "microscopic_data" in data:
                sections.append(analyze_microscopic(data.get("microscopic_data", {})))
        elif test_type == "culture":
            micro = data.get("micro_data", {})
            sections.append(analyze_microbiology(
                bacterial_load=micro.get("bacterial_load", 0),
                microbial_composition=micro.get("microbial_composition", {}),
                detected_pathogens=micro.get("detected_pathogens", []),
                resistance_genes=micro.get("resistance_genes", []),
                symptoms=micro.get("symptoms", False)
            ))
        elif test_type == "24-hour":
            sections.append("24-Hour Volume Analysis: " + analyze_24hour_volume(data.get("urine_volume")))
        elif test_type == "pregnancy":
            sections.append(analyze_pregnancy_test(data.get("pregnancy_data", {})))
        else:  # full integration
            if "micro_data" in data:
                micro = data.get("micro_data", {})
                sections.append(analyze_microbiology(
                    bacterial_load=micro.get("bacterial_load", 0),
                    microbial_composition=micro.get("microbial_composition", {}),
                    detected_pathogens=micro.get("detected_pathogens", []),
                    resistance_genes=micro.get("resistance_genes", []),
                    symptoms=micro.get("symptoms", False)
                ))
            if "chem_data" in data:
                sections.append(analyze_chemistry(data.get("chem_data", {})))
            if "microscopic_data" in data:
                sections.append(analyze_microscopic(data.get("microscopic_data", {})))
            if "urine_volume" in data:
                sections.append("24-Hour Volume: " + analyze_24hour_volume(data.get("urine_volume")))
            if "rapid_data" in data:
                sections.append(analyze_rapid_urine(data.get("rapid_data", {})))
            if "pregnancy_data" in data:
                sections.append(analyze_pregnancy_test(data.get("pregnancy_data", {})))
    except Exception as e:
        logger.error(f"Error in overall urine analysis: {e}")
        sections.append("Overall urine analysis error.")
    return "\n".join(sections)

# ---------------------------
# Parsing the Report Text
# ---------------------------
def parse_report_text(text):
    data = {}
    chem_data = {}
    microscopic_data = {}
    micro_data = {}
    rapid_data = {}
    pregnancy_data = {}

    try:
        # Chemical Analysis
        m = re.search(r"pH[:\s]+([\d\.]+)", text, re.IGNORECASE)
        if m: chem_data["pH"] = float(m.group(1))
        m = re.search(r"Color[:\s]+([\w\s]+)", text, re.IGNORECASE)
        if m: chem_data["color"] = m.group(1).strip()
        m = re.search(r"Clarity[:\s]+([\w\s]+)", text, re.IGNORECASE)
        if m: chem_data["clarity"] = m.group(1).strip()
        m = re.search(r"Odor[:\s]+([\w\s]+)", text, re.IGNORECASE)
        if m: chem_data["odor"] = m.group(1).strip()
        m = re.search(r"Specific\s*Gravity[:\s]+([\d\.]+)", text, re.IGNORECASE)
        if m: chem_data["specific_gravity"] = float(m.group(1))
        m = re.search(r"Protein[:\s]+([\d\.]+)\s*mg/dL", text, re.IGNORECASE)
        if m: chem_data["protein"] = float(m.group(1))
        m = re.search(r"Glucose[:\s]+(negative|positive)", text, re.IGNORECASE)
        if m: chem_data["glucose"] = m.group(1).lower()
        m = re.search(r"Ketones[:\s]+(negative|positive)", text, re.IGNORECASE)
        if m: chem_data["ketones"] = m.group(1).lower()
        m = re.search(r"Blood[:\s]+(negative|positive)", text, re.IGNORECASE)
        if m: chem_data["blood"] = m.group(1).lower()
        m = re.search(r"Nitrites[:\s]+(negative|positive)", text, re.IGNORECASE)
        if m: chem_data["nitrites"] = m.group(1).lower()
        m = re.search(r"Leukocyte\s*Esterase[:\s]+(negative|positive)", text, re.IGNORECASE)
        if m: chem_data["leukocyte_esterase"] = m.group(1).lower()
        m = re.search(r"Microalbumin[:\s]+([\d\.]+)\s*mg/day", text, re.IGNORECASE)
        if m: chem_data["microalbumin"] = float(m.group(1))
        if chem_data:
            data["chem_data"] = chem_data
    except Exception as e:
        logger.error(f"Error parsing chemical data: {e}")

    try:
        # Microscopic Analysis
        m = re.search(r"RBC[:\s]+([\d\.]+)", text, re.IGNORECASE)
        if m: microscopic_data["rbc"] = float(m.group(1))
        m = re.search(r"WBC[:\s]+([\d\.]+)", text, re.IGNORECASE)
        if m: microscopic_data["wbc"] = float(m.group(1))
        m = re.search(r"Casts[:\s]+([\w\s]+)", text, re.IGNORECASE)
        if m: microscopic_data["casts"] = m.group(1).strip()
        m = re.search(r"Crystals[:\s]+([\w\s]+)", text, re.IGNORECASE)
        if m: microscopic_data["crystals"] = m.group(1).strip()
        m = re.search(r"Epithelial\s*cells?[:\s]+([\d\.]+)", text, re.IGNORECASE)
        if m: microscopic_data["epithelial_cells"] = float(m.group(1))
        if microscopic_data:
            data["microscopic_data"] = microscopic_data
    except Exception as e:
        logger.error(f"Error parsing microscopic data: {e}")

    try:
        # Microbiology
        m = re.search(r"Bacterial\s*Load[:\s]+([\d\.e\+]+)", text, re.IGNORECASE)
        if m:
            try:
                micro_data["bacterial_load"] = float(m.group(1))
            except:
                micro_data["bacterial_load"] = 0.0
        m = re.search(r"Lactobacillus\s*gasseri[:\s]+([\d\.]+)", text, re.IGNORECASE)
        if m:
            micro_data.setdefault("microbial_composition", {})["lactobacillus gasseri"] = float(m.group(1))
        m = re.search(r"Enterococcus\s*faecalis[:\s]+([\d\.]+)", text, re.IGNORECASE)
        if m:
            micro_data.setdefault("microbial_composition", {})["enterococcus faecalis"] = float(m.group(1))
        m = re.search(r"Actinomyces\s*neuii[:\s]+([\d\.]+)", text, re.IGNORECASE)
        if m:
            micro_data.setdefault("microbial_composition", {})["actinomyces neuii"] = float(m.group(1))
        m = re.search(r"Escherichia\s*coli[:\s]+([\d\.]+)", text, re.IGNORECASE)
        if m:
            micro_data.setdefault("microbial_composition", {})["escherichia coli"] = float(m.group(1))

        detected = []
        for pathogen in ["Escherichia coli", "Klebsiella pneumoniae", "Staphylococcus aureus"]:
            pattern = re.compile(re.escape(pathogen) + r"[:\s]+([\d\.]+)", re.IGNORECASE)
            m = pattern.search(text)
            if m and float(m.group(1)) > 0:
                detected.append(pathogen)
        if detected:
            micro_data["detected_pathogens"] = detected
        if re.search(r"resistance gene", text, re.IGNORECASE):
            micro_data["resistance_genes"] = ["Aminoglycoside resistance gene"]
        if micro_data:
            data["micro_data"] = micro_data
    except Exception as e:
        logger.error(f"Error parsing microbiology data: {e}")

    try:
        # 24-Hour Urine Volume
        m = re.search(r"24[-\s]*(hour|hr)\s*urine\s*volume[:\s]+([\d\.]+)\s*mL", text, re.IGNORECASE)
        if m:
            data["urine_volume"] = float(m.group(2))
    except Exception as e:
        logger.error(f"Error parsing urine volume: {e}")

    try:
        # Rapid Urine Test
        rapid_dict = {}
        for param in ["nitrites", "leukocyte_esterase", "glucose", "protein", "blood"]:
            m = re.search(param + r"[:\s]+(negative|positive)", text, re.IGNORECASE)
            if m:
                rapid_dict[param] = m.group(1).lower()
        if rapid_dict:
            data["rapid_data"] = rapid_dict
    except Exception as e:
        logger.error(f"Error parsing rapid urine data: {e}")

    try:
        # Pregnancy Test
        m = re.search(r"Pregnancy\s*Test[:\s]+(Positive|Negative)", text, re.IGNORECASE)
        if m:
            pregnancy_data["result"] = m.group(1)
        else:
            m = re.search(r"hCG[:\s]+([\d\.]+)\s*mIU/mL", text, re.IGNORECASE)
            if m:
                pregnancy_data["hcg"] = float(m.group(1))
        if pregnancy_data:
            data["pregnancy_data"] = pregnancy_data
    except Exception as e:
        logger.error(f"Error parsing pregnancy data: {e}")

    data["test_type"] = "full"
    return data

# ---------------------------
# Custom Recommendations Mapping
# ---------------------------
RECOMMENDATIONS = {
    # Chemical Dipstick
    "pH is out of the normal range": (
        "Adjust dietary acid load: reduce high-acid foods (e.g., processed meat, soda) and "
        "increase fruits/vegetables to help normalize urine pH."
    ),
    "Color '": (
        "Increase hydration and avoid foods/medications that can discolor urine (e.g., beets, rifampin)."
    ),
    "Clarity": (
        "Maintain good fluid intake; if cloudiness persists, consider evaluation for infection or crystalluria."
    ),
    "Odor": (
        "Practice good hygiene; if a foul odor continues, seek evaluation for urinary tract infection."
    ),
    "Specific Gravity": (
        "Ensure adequate hydration; aim for 1.5–2 L of water per day unless contraindicated."
    ),
    "Protein level": (
        "Control blood pressure and blood sugar; consider reducing salt intake and discuss ACE inhibitors with your doctor."
    ),
    # Microscopy
    "RBC count": (
        "Rule out stones or trauma; increase hydration and discuss imaging with your provider if bleeding persists."
    ),
    "WBC count": (
        "Suspect infection; consider a urine culture and appropriate antibiotics under medical supervision."
    ),
    "casts": (
        "Follow up for possible renal pathology; ensure hydration and consult nephrology if casts persist."
    ),
    "crystals": (
        "Increase fluid intake; dietary modifications depending on crystal type (e.g., reduce oxalate for calcium oxalate stones)."
    ),
    "Epithelial cells": (
        "May indicate contamination—ensure clean-catch technique or repeat sample."
    ),
    # Microbiology
    "High bacterial load": (
        "Start targeted antibiotics based on culture sensitivities; hydrate and monitor symptoms."
    ),
    "Low proportion of beneficial bacteria": (
        "Consider a probiotic with Lactobacillus spp. and dietary fiber to support healthy flora."
    ),
    "Detected common pathogens": (
        "Treat identified pathogen(s) with appropriate antibiotics as per local guidelines."
    ),
    "Resistance genes detected": (
        "Notify your physician to choose antibiotics not compromised by detected resistance."
    ),
    # Volume
    "is low (oliguria)": (
        "Assess hydration status—gently increase fluid intake; if oliguria persists, evaluate renal function."
    ),
    "is high (polyuria)": (
        "Monitor fluid balance; evaluate for diabetes mellitus or endocrine causes if excessive."
    ),
    # Rapid & Pregnancy
    "Rapid Urine Test: Abnormal": (
        "Follow up abnormal dipstick findings with microscopy and culture; consult your clinician."
    ),
    "Pregnancy Test: Positive": (
        "Confirm with quantitative hCG and schedule obstetric evaluation early in pregnancy."
    ),
}

# ---------------------------
# Analyze Urine Report File
# ---------------------------
def analyze_urine_report_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        text = extract_text(file_path, ext)
        if not text:
            return "No text could be extracted from the file."
    except Exception as e:
        logger.error(f"Error during text extraction: {e}")
        return "Error during text extraction."

    try:
        parsed_data = parse_report_text(text)
    except Exception as e:
        logger.error(f"Error parsing report text: {e}")
        return "Error parsing the report data."

    try:
        analysis_report = analyze_urine_test(parsed_data)
    except Exception as e:
        logger.error(f"Error during urine test analysis: {e}")
        analysis_report = "Error during urine analysis."

    # Build targeted recommendations
    recs = []
    for phrase, advice in RECOMMENDATIONS.items():
        if phrase.lower() in analysis_report.lower():
            recs.append(f"- {advice}")

    if recs:
        recommendation_block = "\n\n[Recommendations]\n" + "\n".join(recs)
    else:
        recommendation_block = (
            "\n\n[Recommendations] All parameters are within normal limits. "
            "Continue your current healthy regimen."
        )

    return analysis_report + recommendation_block

# ---------------------------
# Flask Routes
# ---------------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path and os.path.exists(os.path.join(app.template_folder, path)):
        return send_from_directory(app.template_folder, path)
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/diagnostics/upload', methods=['POST'])
def upload():
    if 'report' not in request.files:
        abort(400, 'No file part in the request')
    f = request.files['report']
    if not f.filename:
        abort(400, 'No file selected')
    filename = secure_filename(f.filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXT:
        abort(400, 'Unsupported file format')
    save_name = f"{uuid.uuid4()}{ext}"
    save_path = os.path.join(UPLOAD_DIR, save_name)
    try:
        f.save(save_path)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        abort(500, "Error saving the uploaded file.")

    analysis = analyze_urine_report_file(save_path)

    try:
        os.remove(save_path)
    except OSError as e:
        request.logger.error(f"Error removing file: {e}")

    return jsonify({
        'reportId': request.cid,
        'analysis': {
            'status': 'processed',
            'port': PORT,
            'report': analysis
        }
    })

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Handles file upload and displays analysis results.
    """
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file and uploaded_file.filename:
            file_path = os.path.join('uploads', uploaded_file.filename)
            uploaded_file.save(file_path)
            result = analyze_urine_report_file(file_path)
            os.remove(file_path)  # Clean up uploaded file after processing
            return render_template('result.html', result=result)
        else:
            return render_template('index.html', error="No file selected.")
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'correlationId': request.cid})

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found', 'correlationId': request.cid}), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': str(e), 'correlationId': request.cid}), 400

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal Server Error', 'correlationId': request.cid}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)

