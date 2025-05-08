import logging
from reference import REFERENCE
from units import normalize_unit, convert_value

logger = logging.getLogger('BloodAnalysis')

ADVICE = {
    "hemoglobin": {
        "low": "Eat more iron-rich foods (leafy greens, red meat, beans, lentils) and vitamin C-rich fruits (oranges, guava) to improve absorption.",
        "high": "Stay hydrated. High hemoglobin may need medical evaluation."
    },
    "mch": {
        "low": "Low MCH may indicate iron deficiency. Eat more iron-rich foods.",
        "high": "Consult your doctor for further evaluation."
    },
    "mchc": {
        "low": "Low MCHC may indicate iron deficiency anemia. Eat more iron-rich foods and vitamin C-rich fruits.",
        "high": "Consult your doctor for further evaluation."
    },
    # Add more as needed...
}

def analyze_and_recommend(results, gender="male"):
    health_status = "Healthy"
    abnormal_advice = []
    gender = gender.lower()
    abnormal_found = False

    for test_key, data in results.items():
        ref = REFERENCE.get(test_key)
        if not ref:
            logger.warning(f"No reference for {test_key}")
            continue
        try:
            value = float(data["value"])
        except Exception:
            logger.error(f"Could not parse value for {test_key}: {data['value']}")
            continue
        unit = normalize_unit(data["unit"])
        ref_range = ref.get(gender, ref.get("male"))
        low, high = ref_range["range"]
        ref_unit = normalize_unit(ref_range["unit"])
        value_converted = convert_value(value, unit, ref_unit, test_key)
        logger.info(f"Comparing {test_key}: {value_converted} {ref_unit} (ref: {low}-{high} {ref_unit})")
        if value_converted < low:
            health_status = "Abnormal"
            abnormal_found = True
            msg = f"{test_key.title()} is LOW ({value_converted} {ref_unit}, normal: {low}-{high} {ref_unit})."
            diet = ADVICE.get(test_key, {}).get("low", "")
            if diet:
                msg += " Recommendation: " + diet
            abnormal_advice.append(msg)
        elif value_converted > high:
            health_status = "Abnormal"
            abnormal_found = True
            msg = f"{test_key.title()} is HIGH ({value_converted} {ref_unit}, normal: {low}-{high} {ref_unit})."
            diet = ADVICE.get(test_key, {}).get("high", "")
            if diet:
                msg += " Recommendation: " + diet
            abnormal_advice.append(msg)
        # If normal, do not display

    if not abnormal_found:
        return "Health Status: Healthy\n\nAll your test results are within normal ranges. Keep up your healthy lifestyle!"
    else:
        return f"Health Status: Abnormal\n\n" + "\n\n".join(abnormal_advice)
