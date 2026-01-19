from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
from pathlib import Path
import os
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# TOPSIS Functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def topsis_calculation(df, weights, impacts):
    """
    Perform TOPSIS calculation
    """
    # Normalize the matrix
    normalized_df = df.copy()
    for col in df.columns[1:]:
        sum_of_squares = np.sqrt((df[col] ** 2).sum())
        if sum_of_squares != 0:
            normalized_df[col] = df[col] / sum_of_squares
        else:
            normalized_df[col] = 0
    
    # Apply weights
    weighted_df = normalized_df.copy()
    for idx, col in enumerate(normalized_df.columns[1:]):
        weighted_df[col] = normalized_df[col] * weights[idx]
    
    # Find ideal best and worst
    ideal_best = []
    ideal_worst = []
    for idx, col in enumerate(weighted_df.columns[1:]):
        if impacts[idx] == '+':
            ideal_best.append(weighted_df[col].max())
            ideal_worst.append(weighted_df[col].min())
        else:
            ideal_best.append(weighted_df[col].min())
            ideal_worst.append(weighted_df[col].max())
    
    # Calculate distances
    distance_best = []
    distance_worst = []
    
    for i in range(len(weighted_df)):
        dist_best = 0
        dist_worst = 0
        
        for j, col in enumerate(weighted_df.columns[1:]):
            dist_best += (weighted_df.iloc[i][col] - ideal_best[j]) ** 2
            dist_worst += (weighted_df.iloc[i][col] - ideal_worst[j]) ** 2
        
        distance_best.append(np.sqrt(dist_best))
        distance_worst.append(np.sqrt(dist_worst))
    
    # Calculate TOPSIS scores
    topsis_scores = []
    for i in range(len(distance_best)):
        denominator = distance_best[i] + distance_worst[i]
        if denominator == 0:
            topsis_scores.append(0)
        else:
            topsis_scores.append(distance_worst[i] / denominator)
    
    # Add scores and ranks
    result_df = df.copy()
    result_df['Topsis Score'] = topsis_scores
    result_df['Rank'] = result_df['Topsis Score'].rank(ascending=False).astype(int)
    
    return result_df

def send_email_with_attachment(recipient_email, result_file):
    """
    Send email with TOPSIS result as attachment
    NOTE: You need to configure SMTP settings
    """
    # Email configuration (UPDATE THESE!)
    sender_email = "lbhatia_be23@thapar.edu"  # Replace with your email
    sender_password = "ywjo zgdn axut jiix"   # Replace with app password
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = 'TOPSIS Analysis Results'
    
    # Email body
    body = """
    Hello,
    
    Your TOPSIS analysis has been completed successfully!
    
    Please find the results attached in the CSV file.
    
    Thank you for using TOPSIS Analysis Tool.
    
    Best regards,
    TOPSIS Team
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach file
    with open(result_file, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(result_file)}')
        msg.attach(part)
    
    # Send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

@app.route('/')
def home():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle TOPSIS analysis request"""
    try:
        # Get form data
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        weights_str = request.form.get('weights', '')
        impacts_str = request.form.get('impacts', '')
        email = request.form.get('email', '')
        
        # Validate inputs
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not email or not validate_email(email):
            return jsonify({'success': False, 'message': 'Invalid email address'}), 400
        
        # Parse weights and impacts
        try:
            weights = [float(w.strip()) for w in weights_str.split(',')]
        except:
            return jsonify({'success': False, 'message': 'Invalid weights format'}), 400
        
        try:
            impacts = [i.strip() for i in impacts_str.split(',')]
        except:
            return jsonify({'success': False, 'message': 'Invalid impacts format'}), 400
        
        # Validate impacts
        for impact in impacts:
            if impact not in ['+', '-']:
                return jsonify({'success': False, 'message': 'Impacts must be + or -'}), 400
        
        # Check if weights and impacts match
        if len(weights) != len(impacts):
            return jsonify({'success': False, 'message': 'Number of weights must equal number of impacts'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read file
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                return jsonify({'success': False, 'message': 'File must be CSV or Excel'}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error reading file: {str(e)}'}), 400
        
        # Validate data
        if df.shape[1] < 3:
            return jsonify({'success': False, 'message': 'File must have at least 3 columns'}), 400
        
        num_criteria = df.shape[1] - 1
        if len(weights) != num_criteria:
            return jsonify({'success': False, 'message': f'Number of weights ({len(weights)}) must equal criteria ({num_criteria})'}), 400
        
        # Check numeric columns
        for col in df.columns[1:]:
            if not pd.api.types.is_numeric_dtype(df[col]):
                return jsonify({'success': False, 'message': f'Column {col} must be numeric'}), 400
        
        # Perform TOPSIS calculation
        result_df = topsis_calculation(df, weights, impacts)
        
        # Save result
        result_filename = f'result_{Path(filename).stem}.xlsx'
        result_filepath = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
        result_df.to_excel(result_filepath, index=False)

        
        # Send email
        email_sent = send_email_with_attachment(email, result_filepath)
        
        if email_sent:
            return jsonify({
                'success': True, 
                'message': 'Analysis completed! Results sent to your email.',
                'result_file': result_filename
            })
        else:
            # If email fails, still return results but with warning
            return jsonify({
                'success': True,
                'message': 'Analysis completed! Email sending failed. Please contact support.',
                'result_file': result_filename
            })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/download/<filename>')
def download(filename):
    """Download result file"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'success': False, 'message': 'File not found'}), 404

if __name__ == '__main__':
    print("🚀 Starting TOPSIS Web Server...")
    print("📍 Access at: http://localhost:5000")
    print("⚠️  Remember to configure email settings in the code!")
    app.run(debug=True, host='0.0.0.0', port=5000)
