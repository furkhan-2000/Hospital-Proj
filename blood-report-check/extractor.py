import re
import logging

logger = logging.getLogger('BloodAnalysis')

BLOOD_TESTS = [
    "hemoglobin", "hb", "hgb", "hematocrit", "hct", "rbc", "red blood cell",
    "wbc", "white blood cell", "platelet", "platelets", "neutrophils",
    "lymphocytes", "eosinophils", "monocytes", "basophils", "fasting plasma glucose",
    "2-hour postprandial glucose", "glucose", "hba1c", "total cholesterol",
    "ldl cholesterol", "hdl cholesterol", "triglycerides", "total bilirubin",
    "alt", "sgpt", "ast", "sgot", "alp", "albumin", "serum creatinine",
    "creatinine", "bun", "blood urea nitrogen", "egfr", "sodium", "tsh",
    "free t4", "total t3", "serum iron", "iron", "ferritin", "tibc",
    "troponin-i", "ck-mb", "bnp", "crp", "esr", "pt", "inr", "aptt", "mch", "mchc"
]

SKIP_WORDS = ["reference", "range", "unit", "normal", "interval", "ref.",
             "biological", "test", "parameter", "result", "value"]

EXPECTED_RANGES = {
    "mch": (10, 50),      # pg
    "mchc": (20, 45),     # g/dL or %
    "hemoglobin": (5, 20) # g/dL
}

# Precompiled regex patterns
TEST_PATTERN = re.compile(r'\b(' + '|'.join(map(re.escape, BLOOD_TESTS)) + r')\b')
SKIP_RE = re.compile(r'\b(' + '|'.join(map(re.escape, SKIP_WORDS)) + r')\b')
VALUE_UNIT_RE = re.compile(r'(\d+[\.,]?\d*)\s*([a-zA-Z%/µ²³\-]*)')
NORMALIZE_RE = re.compile(r'[^a-z0-9]')

# Precomputed mappings
TEST_TO_KEY = {test: NORMALIZE_RE.sub('', test) for test in BLOOD_TESTS}

def clean_lines(text):
    return [re.sub(r'\s+', ' ', line.strip()).lower()
            for line in text.splitlines() if line.strip()]

def correct_value(test_key, value):
    try:
        v = float(value.replace(',', '.'))
        if test_key in EXPECTED_RANGES:
            min_v, max_v = EXPECTED_RANGES[test_key]
            for factor in [10, 100]:
                if min_v <= (corrected := v/factor) <= max_v:
                    return f"{corrected:.2f}"
        return f"{v:.2f}"
    except ValueError:
        return value

def extract_entities(text):
    results = {}
    lines = clean_lines(text)

    for i, line in enumerate(lines):
        if SKIP_RE.search(line):
            continue

        for match in TEST_PATTERN.finditer(line):
            test_name = match.group()
            test_key = TEST_TO_KEY[test_name]

            if test_key in results:
                continue

            # Look in current line first
            value_match = VALUE_UNIT_RE.search(line[match.end():])
            if value_match:
                value, unit = value_match.groups()
                results[test_key] = {
                    "value": correct_value(test_key, value),
                    "unit": unit.strip()
                }
                continue

            # Check next 1 line (reduced from 2 to save resources)
            for j in range(1, 2):
                if i+j >= len(lines):
                    break
                if not SKIP_RE.search(lines[i+j]):
                    if value_match := VALUE_UNIT_RE.search(lines[i+j]):
                        value, unit = value_match.groups()
                        results[test_key] = {
                            "value": correct_value(test_key, value),
                            "unit": unit.strip()
                        }
                        break

    if not results:
        logger.warning("No results extracted. Check OCR quality.")

    return results
