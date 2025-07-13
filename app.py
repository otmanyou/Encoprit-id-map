from flask import Flask, request, send_file, render_template_string, jsonify, redirect, url_for
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import time
import os
import string
import random
from datetime import datetime, timedelta

app = Flask(__name__)
executor = ThreadPoolExecutor(4)  # For handling multiple requests

# Temporary storage directory
TEMP_DIR = "temp_files"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Cleanup function for temporary files
def cleanup_temp_files():
    now = datetime.now()
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        try:
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if now - creation_time > timedelta(minutes=5):
                os.remove(file_path)
        except:
            pass

# Generate random filename
def generate_random_filename(original_name):
    rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    return f"{rand_str}_{original_name}"

# Encryption function
def encrypt_id(x):
    try:
        x = int(x)
        dec = ['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', 
               '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f',
               'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af',
               'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf',
               'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf',
               'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df',
               'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef',
               'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']
        xxx = ['1', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f',
               '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f',
               '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f',
               '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f',
               '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f',
               '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f',
               '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f',
               '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']
        
        x = x / 128
        if x > 128:
            x = x / 128
            if x > 128:
                x = x / 128
                if x > 128:
                    x = x / 128
                    strx = int(x)
                    y = (x - int(strx)) * 128
                    stry = str(int(y))
                    z = (y - int(stry)) * 128
                    strz = str(int(z))
                    n = (z - int(strz)) * 128
                    strn = str(int(n))
                    m = (n - int(strn)) * 128
                    return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
                else:
                    strx = int(x)
                    y = (x - int(strx)) * 128
                    stry = str(int(y))
                    z = (y - int(stry)) * 128
                    strz = str(int(z))
                    n = (z - int(strz)) * 128
                    strn = str(int(n))
                    return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
        return None
    except:
        return None

# File processing function
def process_file(file_content, encrypted_id):
    combined_code = "38" + encrypted_id
    combined_bytes = bytes.fromhex(combined_code)
    
    modified_content = bytearray(file_content)
    index = modified_content.find(combined_bytes)
    
    while index != -1:
        del modified_content[index:index+len(combined_bytes)]
        index = modified_content.find(combined_bytes)
    
    return modified_content

# API endpoint
@app.route('/api/process', methods=['POST'])
def api_process():
    if 'file' not in request.files or not request.form.get('id'):
        return jsonify({'error': 'Missing file or ID'}), 400
    
    file = request.files['file']
    user_id = request.form['id']
    
    if not file.filename.endswith('.bytes'):
        return jsonify({'error': 'Invalid file format. Only .bytes files are allowed'}), 400
    
    encrypted_id = encrypt_id(user_id)
    if not encrypted_id:
        return jsonify({'error': 'Failed to encrypt ID'}), 400
    
    try:
        file_content = file.read()
        modified_content = process_file(file_content, encrypted_id)
        
        # Generate random filename
        random_filename = generate_random_filename(file.filename)
        temp_filepath = os.path.join(TEMP_DIR, random_filename)
        
        # Save to temporary file
        with open(temp_filepath, 'wb') as f:
            f.write(modified_content)
        
        # Return the temporary download link
        download_url = url_for('download_file', filename=random_filename, _external=True)
        
        return jsonify({
            'success': True,
            'download_url': download_url,
            'filename': random_filename,
            'expires_in': 20  # seconds
        })
    except Exception as e:
        return jsonify({'error': f'File processing failed: {str(e)}'}), 500

# Download endpoint for temporary files
@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(TEMP_DIR, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return "File not found or link expired", 404
            
        # Check file age (should be less than 20 seconds)
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(filepath))
        if file_age.total_seconds() > 20:
            os.remove(filepath)  # Delete expired file
            return "Download link has expired", 410  # Gone
        
        # Send the file
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

# Website interface
@app.route('/', methods=['GET'])
def index():
    # Clean up old files on each visit
    cleanup_temp_files()
    return render_template_string(HTML_TEMPLATE)

# Complete HTML template with CSS and JS
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bytes File Encryption Tool</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #1a1a1a;
            --secondary-color: #2d2d2d;
            --accent-color: #4fc3f7;
            --dark-color: #0a0a0a;
            --light-color: #f0f0f0;
            --success-color: #4caf50;
            --error-color: #f44336;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transition: all 0.3s ease;
        }
        
        body {
            background: #000 url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none"><text x="0" y="50" font-family="monospace" font-size="10" fill="rgba(79,195,247,0.05)">01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101 01010101</text></svg>');
            color: var(--light-color);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 30px;
        }
        
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: var(--accent-color);
            text-decoration: none;
            display: flex;
            align-items: center;
        }
        
        .logo i {
            margin-left: 10px;
        }
        
        .main-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(5px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        h1 {
            font-size: 36px;
            margin-bottom: 20px;
            text-align: center;
            color: var(--accent-color);
        }
        
        .description {
            text-align: center;
            margin-bottom: 30px;
            line-height: 1.6;
            opacity: 0.9;
            max-width: 800px;
        }
        
        .upload-container {
            width: 100%;
            max-width: 600px;
            margin-bottom: 30px;
        }
        
        .file-upload {
            border: 2px dashed rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            background: rgba(30, 30, 30, 0.3);
        }
        
        .file-upload:hover {
            border-color: var(--accent-color);
        }
        
        .file-upload i {
            font-size: 50px;
            color: var(--accent-color);
            margin-bottom: 15px;
        }
        
        .file-upload p {
            margin-bottom: 15px;
        }
        
        .file-upload input {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            cursor: pointer;
        }
        
        .id-input {
            width: 100%;
            max-width: 400px;
            margin-bottom: 30px;
        }
        
        .id-input input {
            width: 100%;
            padding: 15px 20px;
            border-radius: 8px;
            border: none;
            background: rgba(255, 255, 255, 0.1);
            color: var(--light-color);
            font-size: 16px;
            outline: none;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .id-input input:focus {
            background: rgba(255, 255, 255, 0.2);
            box-shadow: 0 0 0 2px var(--accent-color);
            border-color: transparent;
        }
        
        .btn {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .btn:hover {
            background: var(--secondary-color);
        }
        
        .btn i {
            margin-left: 8px;
        }
        
        .btn-accent {
            background: var(--accent-color);
            color: var(--dark-color);
            font-weight: bold;
        }
        
        .btn-accent:hover {
            background: #3fb0e6;
        }
        
        .result-container {
            margin-top: 30px;
            width: 100%;
            max-width: 600px;
            display: none;
        }
        
        .result-box {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .download-btn {
            margin-top: 15px;
        }
        
        .social-links {
            display: flex;
            justify-content: center;
            margin-top: 40px;
            gap: 15px;
        }
        
        .social-link {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--light-color);
            font-size: 20px;
            text-decoration: none;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .social-link:hover {
            transform: translateY(-3px);
        }
        
        .youtube:hover {
            background: #ff0000;
        }
        
        .tiktok:hover {
            background: #000000;
        }
        
        .telegram:hover {
            background: #0088cc;
        }
        
        footer {
            text-align: center;
            padding: 30px 0;
            margin-top: 50px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 14px;
            opacity: 0.7;
        }
        
        @media (max-width: 768px) {
            header {
                flex-direction: column;
                text-align: center;
            }
            
            .logo {
                margin-bottom: 15px;
            }
            
            h1 {
                font-size: 28px;
            }
            
            .file-upload {
                padding: 30px 20px;
            }
        }
        
        .spinner {
            display: none;
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            border-top: 4px solid var(--accent-color);
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            color: var(--error-color);
            margin-top: 10px;
            text-align: center;
        }
        
        .progress-container {
            width: 100%;
            max-width: 400px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
            margin: 20px 0;
            display: none;
        }
        
        .progress-bar {
            height: 10px;
            background: var(--accent-color);
            border-radius: 5px;
            width: 0%;
            transition: width 0.3s;
        }
        
        .progress-text {
            text-align: center;
            margin-top: 5px;
            font-size: 12px;
        }
        
        .btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        .copy-link {
            display: flex;
            align-items: center;
            margin-top: 15px;
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 8px;
            width: 100%;
        }
        
        .copy-link input {
            flex: 1;
            background: transparent;
            border: none;
            color: white;
            padding: 5px;
            outline: none;
        }
        
        .copy-link button {
            background: var(--accent-color);
            border: none;
            color: var(--dark-color);
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            margin-left: 5px;
        }
        
        .copy-link button:hover {
            background: #3fb0e6;
        }
        
        .expiry-timer {
            margin-top: 10px;
            font-size: 14px;
            color: #ff9800;
        }
        
        .download-section {
            margin-top: 20px;
            width: 100%;
            text-align: center;
        }
        
        .download-link {
            display: inline-block;
            margin-top: 10px;
            color: var(--accent-color);
            text-decoration: none;
            word-break: break-all;
            padding: 10px;
            background: rgba(79, 195, 247, 0.1);
            border-radius: 5px;
        }
        
        .download-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <a href="#" class="logo">
                CRAFTLAND EDIT MAP FILE
            </a>
        </header>
        
        <main class="main-content">
            <h1>MED BY ╭ᶫ⁷╯Ｌ７ＡＪ ¹</h1>
            
            <p class="description">
               Upload the file below and put the ID  
            </p>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-container">
                    <div class="file-upload">
                        <input type="file" id="fileInput" name="file" accept=".bytes" required>
                        <i class="fas fa-cloud-upload-alt"></i>
                        <p>Upload the file  .bytes ></p>
                        <span id="fileName">No file chosen</span>
                    </div>
                </div>
                
                <div class="id-input">
                    <input type="text" id="idInput" name="id" placeholder="Enter ID" required>
                </div>
                
                <button type="submit" class="btn btn-accent" id="submitBtn">
                    Process File
                    <i class="fas fa-cogs"></i>
                </button>
            </form>
            
            <div class="progress-container" id="progressContainer">
                <div class="progress-bar" id="progressBar"></div>
                <div class="progress-text" id="progressText">Processing...</div>
            </div>
            
            <div class="spinner" id="spinner"></div>
            
            <div class="result-container" id="resultContainer">
                <div class="result-box">
                    <p id="resultMessage">File processed successfully!</p>
                    <div class="download-section">
                        <p>Your file is ready to download:</p>
                        <a href="#" id="downloadLink" class="download-link" target="_blank"></a>
                    </div>
                    <div class="expiry-timer" id="expiryTimer"></div>
                    <button class="btn download-btn" id="downloadBtn">
                        Download Now
                        <i class="fas fa-download"></i>
                    </button>
                </div>
            </div>
            
            <div class="error" id="errorMessage"></div>
        </main>
        
        <div class="social-links">
            <a href="https://youtube.com/@l7aj.1m?si=sgcsPUwAhqj_agcN" class="social-link youtube" target="_blank">
                <i class="fab fa-youtube"></i>
            </a>
            <a href="https://www.tiktok.com/@l7aj..1m?_t=ZM-8xnsOLMv6GM&_r=1" class="social-link tiktok" target="">
                <i class="fab fa-tiktok"></i>
            </a>
            <a href="https://t.me/l7_l7aj" class="social-link telegram" target="_blank">
                <i class="fab fa-telegram"></i>
            </a>
        </div>
        
        <footer>
            <p> ╭ᶫ⁷╯Ｌ７ＡＪ ¹ ©</p>
        </footer>
    </div>
    
    <script>
        // DOM elements
        const fileInput = document.getElementById('fileInput');
        const fileName = document.getElementById('fileName');
        const submitBtn = document.getElementById('submitBtn');
        const spinner = document.getElementById('spinner');
        const errorMessage = document.getElementById('errorMessage');
        const uploadForm = document.getElementById('uploadForm');
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const resultContainer = document.getElementById('resultContainer');
        const downloadBtn = document.getElementById('downloadBtn');
        const downloadLink = document.getElementById('downloadLink');
        const expiryTimer = document.getElementById('expiryTimer');
        const resultMessage = document.getElementById('resultMessage');

        // File input change handler
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileName.textContent = this.files[0].name;
            } else {
                fileName.textContent = 'No file chosen';
            }
        });

        // Drag and drop functionality
        const uploadContainer = document.querySelector('.file-upload');
        
        uploadContainer.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadContainer.style.borderColor = '#4fc3f7';
        });
        
        uploadContainer.addEventListener('dragleave', () => {
            uploadContainer.style.borderColor = 'rgba(255, 255, 255, 0.2)';
        });
        
        uploadContainer.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadContainer.style.borderColor = 'rgba(255, 255, 255, 0.2)';
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                fileName.textContent = e.dataTransfer.files[0].name;
            }
        });

        // Form submission handler
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const file = fileInput.files[0];
            const id = document.getElementById('idInput').value;
            
            // Validation
            if (!file) {
                showError('Please upload a file first!');
                return;
            }
            
            if (!id || !/^\d+$/.test(id)) {
                showError('Please enter a valid numeric ID!');
                return;
            }
            
            if (!file.name.endsWith('.bytes')) {
                showError('Please upload a .bytes file only!');
                return;
            }
            
            // Disable submit button to prevent multiple submissions
            submitBtn.disabled = true;
            
            // Show loading indicators
            spinner.style.display = 'block';
            progressContainer.style.display = 'block';
            resultContainer.style.display = 'none';
            errorMessage.textContent = '';
            
            // Simulate progress (in a real app, update based on actual progress)
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += 5;
                if (progress > 90) clearInterval(progressInterval);
                updateProgress(progress);
            }, 200);
            
            try {
                const formData = new FormData(uploadForm);
                
                const response = await fetch('/api/process', {
                    method: 'POST',
                    body: formData
                });
                
                clearInterval(progressInterval);
                updateProgress(100);
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Unknown error occurred');
                }
                
                const data = await response.json();
                
                if (!data.success) {
                    throw new Error(data.error || 'Processing failed');
                }
                
                // Show result with download link
                resultContainer.style.display = 'block';
                downloadLink.href = data.download_url;
                downloadLink.textContent = data.download_url;
                
                // Set up download button
                downloadBtn.onclick = function() {
                    window.open(data.download_url, '_blank');
                };
                
                // Start expiry countdown
                let timeLeft = 20;
                expiryTimer.textContent = `Link expires in: ${timeLeft} seconds`;
                
                const countdown = setInterval(() => {
                    timeLeft--;
                    expiryTimer.textContent = `Link expires in: ${timeLeft} seconds`;
                    
                    if (timeLeft <= 0) {
                        clearInterval(countdown);
                        expiryTimer.textContent = 'Link has expired';
                        expiryTimer.style.color = '#f44336';
                        downloadBtn.disabled = true;
                        downloadLink.style.opacity = '0.5';
                        downloadLink.style.pointerEvents = 'none';
                    }
                }, 1000);
                
            } catch (error) {
                console.error('Error:', error);
                showError(`Error: ${error.message}`);
            } finally {
                spinner.style.display = 'none';
                submitBtn.disabled = false;
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                }, 1000);
            }
        });

        function updateProgress(percent) {
            progressBar.style.width = percent + '%';
            progressText.textContent = `Processing... ${percent}%`;
        }

        function showError(message) {
            errorMessage.textContent = message;
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
