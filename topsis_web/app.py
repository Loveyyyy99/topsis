from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
from pathlib import Path
import os
import tempfile
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Use system temp directory (READ-WRITE SAFE)
UPLOAD_DIR = tempfile.gettempdir()

# ---------------- EMAIL VALIDATION ----------------
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ---------------- TOPSIS LOGIC ----------------
def topsis_calculation(df, weights, impacts):

    # Normalize decision matrix
    norm_df = df.copy()
    for col in df.columns[1:]:
        denom = np.sqrt((df[col] ** 2).sum())
        norm_df[col] = df[col] / denom if denom != 0 else 0

    # Normalize weights
    weights = np.array(weights)
    weights = weights / weights.sum()

    # Weighted normalized matrix
    weighted_df = norm_df.copy()
    for i, col in enumerate(df.columns[1:]):
        weighted_df[col] *= weights[i]

    # Ideal best & worst
    ideal_best, ideal_worst = [], []
    for i, col in enumerate(df.columns[1:]):
        if impacts[i] == '+':
            ideal_best.append(weighted_df[col].max())
            ideal_worst.append(weighted_df[col].min())
        else:
            ideal_best.append(weighted_df[col].min())
            ideal_worst.append(weighted_df[col].max())

    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)

    values = weighted_df.iloc[:, 1:].values
    dist_best = np.linalg.norm(values - ideal_best, axis=1)
    dist_worst = np.linalg.norm(values - ideal_worst, axis=1)

    scores = dist_worst / (dist_best + dist_worst)

    result = df.copy()
    result["Topsis Score"] = scores
    result["Rank"] = result["Topsis Score"].rank(
        method="dense", ascending=False
    ).astype(int)

    return result

# ---------------- EMAIL SENDER ----------------
def send_email_with_attachment(recipient_email, filepath):

    sender_email = "lbhatia_be23@thapar.edu"  # Replace with your email
    sender_password = "ywjo zgdn axut jiix"   # Replace with app password


    if not sender_email or not sender_password:
        return False

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = "TOPSIS Analysis Result"

    body = """Hello,

Your TOPSIS analysis is complete.
Please find the attached result file.

Regards,
TOPSIS Tool
"""
    msg.attach(MIMEText(body, "plain"))

    with open(filepath, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(filepath)}",
        )
        msg.attach(part)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Email Error:", e)
        return False

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "message": "No file uploaded"}), 400

        file = request.files["file"]
        weights = request.form.get("weights", "")
        impacts = request.form.get("impacts", "")
        email = request.form.get("email", "")

        if file.filename == "":
            return jsonify({"success": False, "message": "No file selected"}), 400

        if not validate_email(email):
            return jsonify({"success": False, "message": "Invalid email"}), 400

        weights = [float(w.strip()) for w in weights.split(",")]
        impacts = [i.strip() for i in impacts.split(",")]

        if not all(i in ["+", "-"] for i in impacts):
            return jsonify({"success": False, "message": "Impacts must be + or -"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_DIR, filename)

        # Read file directly
        if filename.endswith(".csv"):
            df = pd.read_csv(file)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file)
        else:
            return jsonify({"success": False, "message": "Invalid file type"}), 400

        df.dropna(inplace=True)

        if len(weights) != df.shape[1] - 1:
            return jsonify({"success": False, "message": "Weights count mismatch"}), 400

        for col in df.columns[1:]:
            if not pd.api.types.is_numeric_dtype(df[col]):
                return jsonify({"success": False, "message": f"{col} must be numeric"}), 400

        result_df = topsis_calculation(df, weights, impacts)

        result_name = f"result_{Path(filename).stem}.xlsx"
        result_path = os.path.join(UPLOAD_DIR, result_name)
        result_df.to_excel(result_path, index=False)

        email_sent = send_email_with_attachment(email, result_path)

        return jsonify({
            "success": True,
            "message": "Analysis complete. Email sent." if email_sent else "Analysis complete. Email failed.",
            "result_file": result_name
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(UPLOAD_DIR, filename)
    return send_file(path, as_attachment=True)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("🚀 TOPSIS Server Running")
    print("📍 http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
