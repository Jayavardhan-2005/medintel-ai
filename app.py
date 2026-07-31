from flask import Flask, render_template, request , jsonify
import os
import pdfplumber
import re

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


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
        for page in pdf.pages:
            extracted_text += page.extract_text() or ""

    pattern = r"([A-Za-z\s]+)\s+([\d.]+)\s+([A-Za-z/%]+)"

    parsed_report = []

    for line in extracted_text.split("\n"):
        match = re.search(pattern, line)
        if match:
            parsed_report.append({
                "test": match.group(1).strip(),
                "value": match.group(2),
                "unit": match.group(3)
            })

    print(parsed_report)
    
    return jsonify(parsed_report)


if __name__ == "__main__":
    app.run(debug=True)