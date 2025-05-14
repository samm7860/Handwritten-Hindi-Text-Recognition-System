import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
import ocr_helper
import numpy as np
import cv2
import base64

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "hindi_ocr_default_secret")

@app.route('/')
def index():
    """
    Route for the homepage where users can upload images
    """
    return render_template('index.html')

@app.route('/recognize', methods=['GET', 'POST'])
def recognize():
    """
    Process uploaded image and perform OCR
    """
    # If it's a GET request or no image is uploaded, redirect to home page
    if request.method == 'GET' or 'image' not in request.files:
        flash('Please upload an image first', 'warning')
        return redirect(url_for('index'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('index'))
    
    if not file or not allowed_file(file.filename):
        flash('Invalid file format. Please upload PNG, JPG, or JPEG files', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Read the image
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        
        # Get preprocessing parameters from form
        resize_percent = int(request.form.get('resize', 100))
        blur_amount = int(request.form.get('blur', 0))
        threshold_type = request.form.get('threshold', 'none')
        denoise = request.form.get('denoise') == 'on'
        contrast_enhance = request.form.get('contrast') == 'on'
        morphology = request.form.get('morphology', 'none')
        is_handwritten = request.form.get('handwritten') == 'on'
        
        # If none selected for morphology, set to None for the function
        if morphology == 'none':
            morphology = None
        
        # Preprocess the image with enhanced parameters
        preprocessed_img = ocr_helper.preprocess_image(
            img, 
            resize_percent=resize_percent,
            blur_amount=blur_amount,
            threshold_type=threshold_type,
            denoise=denoise,
            contrast_enhance=contrast_enhance,
            morphology=morphology
        )
        
        # Perform OCR with handwritten parameter
        text, confidence = ocr_helper.recognize_hindi(preprocessed_img, handwritten=is_handwritten)
        
        # Convert images to base64 for displaying in the result page
        _, original_buffer = cv2.imencode('.png', img)
        original_img_b64 = base64.b64encode(original_buffer).decode('utf-8')
        
        _, processed_buffer = cv2.imencode('.png', preprocessed_img)
        processed_img_b64 = base64.b64encode(processed_buffer).decode('utf-8')
        
        return render_template(
            'result.html', 
            original_img=original_img_b64,
            processed_img=processed_img_b64,
            recognized_text=text,
            confidence=confidence,
            handwritten=is_handwritten
        )
        
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        flash(f'Error processing image: {str(e)}', 'danger')
        return redirect(url_for('index'))

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension
    """
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def run():
    import logging
    import webbrowser
    import threading

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000")).start()  #auto open browser

    app.run(host='127.0.0.1', port=5000, debug=False)

