from flask import Flask, render_template, request , jsonify 
import os
import pdfplumber,pymupdf
import re
from med_base import get_parameter_info
from dotenv import load_dotenv
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



def is_valid_test(test_name):
    INVALID_TEST_NAMES = {
        "Page",
        "Passport No",
        "Patient Information",
        "Sample Information",
        "Client Name",
        "Registration",
        "Location",
        "Approved",
        "Printed On",
        "Process At",
        "Ref",
        "Lab Id",
        "Status",
        "Report",
        "Pathology",
        "MD",
        "Scan QR",
        "Electronically"
    }
    return not any(word in test_name for word in INVALID_TEST_NAMES)


def extract_text_with_ocr(filepath, page_number):

    document = pymupdf.open(filepath)

    page = document[page_number]

    text_page = page.get_textpage_ocr(
        language="eng",
        dpi=200
    )

    text = text_page.extractText()

    document.close()

    return text


def parse_report(extracted_text):

    parsed_report = []

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in extracted_text.split("\n")
        if line.strip()
    ]

    known_tests = {
        "hemoglobin (hb)": "Hemoglobin",
        "hemoglobin": "Hemoglobin",

        "total rbc count": "RBC Count",
        "rbc count": "RBC Count",

        "packed cell volume (pcv)": "Hematocrit",
        "packed cell volume": "Hematocrit",
        "hematocrit": "Hematocrit",

        "mean corpuscular volume (mcv)": "MCV",
        "mean corpuscular volume": "MCV",
        "mcv": "MCV",

        "mch": "MCH",

        "mchc": "MCHC",

        "rdw": "RDW CV",

        "total wbc count": "WBC Count",
        "wbc count": "WBC Count",

        "neutrophils": "Neutrophils",
        "neutrophils microscopic": "Neutrophils",

        "lymphocytes": "Lymphocytes",
        "lymphocytes microscopic": "Lymphocytes",

        "eosinophils": "Eosinophils",

        "monocytes": "Monocytes",

        "basophils": "Basophils",

        "platelet count": "Platelet Count",

        "mpv": "MPV"
    }

    test_aliases = sorted(
        known_tests.keys(),
        key=len,
        reverse=True
    )

    valid_units = {
        "g/dl",
        "fl",
        "pg",
        "%",
        "cumm",
        "/cmm",
        "mill/cumm",
        "million/cmm",
        "million/cumm",
        "mm3",
        "/mm3"
    }

    flag_map = {
        "high": "High",
        "h": "High",

        "low": "Low",
        "l": "Low",

        "borderline": "Borderline"
    }

    ignored_lines = {
        "pm",
        "am",
        "blood",
        "dec",
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",

        "primary sample type",
        "blood indices",
        "differential wbc count",
        "platelet count"
    }
    def normalize(text):

        return re.sub(
            r"\s+",
            " ",
            text.lower()
        ).strip()

    def find_test(line):

        normalized = normalize(line)
        if normalized in known_tests:
            return known_tests[normalized]
        
        for alias in test_aliases:
            if normalized.startswith(alias + " "):
                return known_tests[alias]

            if normalized.startswith(alias + "("):
                return known_tests[alias]

        return None

    def extract_result(block):
        value = None
        flag = None
        unit = None
        combined = " ".join(block)

        combined = re.sub(
            r"\s+",
            " ",
            combined
        ).strip()

        combined_lower = combined.lower()
        for flag_text, status in flag_map.items():

            pattern = r"\b" + re.escape(flag_text) + r"\b"

            if re.search(pattern, combined_lower):

                flag = status
                break

        unit_pattern = "|".join(
            re.escape(unit)
            for unit in sorted(
                valid_units,
                key=len,
                reverse=True
            )
        )

        unit_match = re.search(
            rf"\b({unit_pattern})\b",
            combined_lower
        )

        if unit_match:

            unit = unit_match.group(1)

            # Preserve common display format
            if unit == "g/dl":
                unit = "g/dL"

            elif unit == "fl":
                unit = "fL"

            elif unit == "pg":
                unit = "pg"

            elif unit == "cumm":
                unit = "cumm"

            elif unit == "mill/cumm":
                unit = "mill/cumm"

            elif unit == "million/cmm":
                unit = "million/cmm"

        number_matches = re.finditer(
            r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])",
            combined
        )

        candidates = []

        for match in number_matches:

            number = match.group()

            start = match.start()
            end = match.end()

            before = combined[max(0, start - 3):start]
            after = combined[end:end + 3]

            if "-" in before or "-" in after:

                continue

            context = combined[
                max(0, start - 8):
                min(len(combined), end + 8)
            ].lower()

            if "dec" in context:
                continue

            if "jan" in context:
                continue

            if "feb" in context:
                continue

            if "age" in context:
                continue

            if "pid" in context:
                continue

            if "registered" in context:
                continue

            if "collected" in context:
                continue

            if "reported" in context:
                continue

            candidates.append(number)

        if candidates:

            value = candidates[0]

        return value, flag, unit

    i = 0

    while i < len(lines):

        current_line = lines[i]
        current_normalized = normalize(current_line)

        if current_normalized in ignored_lines:

            i += 1
            continue

        test = find_test(current_line)

        if test is None and i + 1 < len(lines):

            next_line = lines[i + 1]

            next_test = find_test(next_line)

            if next_test is not None:

                test = next_test

                i += 1

        if test is None:

            i += 1
            continue

        block = [current_line]

        # If we advanced to the actual test line,
        # include it.
        if block[-1] != lines[i]:

            block.append(lines[i])

        for j in range(
            i + 1,
            min(i + 7, len(lines))
        ):

            candidate = lines[j]

            candidate_normalized = normalize(candidate)

            # Stop if another supported test begins.
            if find_test(candidate) is not None:

                break

            # Stop at major section headings.
            if candidate_normalized in {
                "blood indices",
                "differential wbc count",
                "platelet count"
            }:

                break

            block.append(candidate)

        value, flag, unit = extract_result(block)
        if value is not None:

            if flag == "High":

                status = "High"

            elif flag == "Low":

                status = "Low"

            elif flag == "Borderline":

                status = "Borderline"

            else:

                status = "Normal"

            parsed_report.append({
                "test": test,
                "flag": flag,
                "status": status,
                "value": value,
                "unit": unit or ""
            })
        i += 1
    return parsed_report

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["report"]

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    extracted_text = ""

    with pdfplumber.open(filepath) as pdf:
        for page_number, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""

            if len(page_text.strip()) < 20:

                print(
                    f"Page {page_number + 1}: "
                    f"Little/no text found. Running OCR..."
                )

                ocr_text = extract_text_with_ocr(
                    filepath,
                    page_number
                )

                extracted_text += ocr_text + "\n"

            else:

                print(
                    f"Page {page_number + 1}: "
                    f"Text extracted normally."
                )

                extracted_text += page_text + "\n"

    parsed_report = parse_report(extracted_text)
    normal_count = 0
    high_count = 0
    low_count = 0
    borderline_count = 0

    for item in parsed_report:

        if item["status"] == "Normal":
            normal_count += 1

        elif item["status"] == "High":
            high_count += 1

        elif item["status"] == "Low":
            low_count += 1

        elif item["status"] == "Borderline":
            borderline_count += 1

    return render_template(
        "analysis.html",
        report=parsed_report,
        normal=normal_count,
        high=high_count,
        low=low_count,
        borderline=borderline_count
    )

@app.route("/explain", methods=["POST"])
def explain():
    data = request.get_json()

    test = data.get("test")
    value = data.get("value")
    unit = data.get("unit")
    status = data.get("status")

    # Get information from our medical knowledge base
    knowledge = get_parameter_info(test)

    # Default fallback explanation
    ai_explanation = knowledge.get(
        "guidance",
        "This result should be interpreted alongside other laboratory results, symptoms, and clinical history."
    )

    # Try Gemini if the API is configured
    if gemini_client:
        try:
            prompt = f"""
You are an educational medical report explanation assistant.

Your job is to explain a laboratory result to a person with no medical background.

Laboratory result:
Test: {test}
Result: {value} {unit}
Status: {status}

Medical knowledge available:
Description: {knowledge.get("description", "")}

Possible reasons for a LOW result:
{", ".join(knowledge.get("low", []))}

Possible reasons for a HIGH result:
{", ".join(knowledge.get("high", []))}

Why this test is performed:
{knowledge.get("why_tested", "")}

Write a short, clear explanation of this specific result.

Follow these rules:

1. Start with the exact heading:
What is it?

Then briefly explain what the test measures.

2. Then use the exact heading:
What does this result mean?

Explain what the supplied result ({value} {unit}) and status ({status}) mean in simple language.

3. If the result is HIGH, use the exact heading:
Why might it be high?

Mention only the most relevant possible causes from the provided medical knowledge.

4. If the result is LOW, use the exact heading:
Why might it be low?

Mention only the most relevant possible causes from the provided medical knowledge.

5. If the result is NORMAL, do not list causes of abnormal results. Instead briefly explain what the normal status generally means.

6. Use the exact heading:
Important note

Explain that a laboratory result alone does not establish a diagnosis and should be interpreted together with symptoms, medical history, other test results, and the laboratory's reference range by a healthcare professional.

7. Do not diagnose the patient.

8. Do not recommend specific medicines, supplements, dosages, or treatments.

9. Do not tell the user to start, stop, or change any medication.

10. Keep the explanation concise and easy to understand.

11. Use plain text only.

12. Do NOT use Markdown.

13. Do NOT use asterisks, bullet points, numbered lists, emojis, or special formatting.

14. Do not invent reference ranges or medical facts that are not provided above.

Return only the explanation.
"""

            response = gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            if response.text:
                ai_explanation = response.text

        except Exception as e:
            print(f"Gemini explanation failed: {e}")

    return jsonify({
        "knowledge": knowledge,
        "ai_explanation": ai_explanation,
        "test": test,
        "value": value,
        "unit": unit,
        "status": status
    })

@app.route("/test-knowledge/<test_name>")
def test_knowledge(test_name):

    info = get_parameter_info(test_name)
    if not info:
        return jsonify({
            "error": "Parameter not found"
        }), 404

    return jsonify(info)

if __name__ == "__main__":
    app.run(debug=True)