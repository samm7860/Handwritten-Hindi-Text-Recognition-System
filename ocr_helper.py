import cv2
import numpy as np
import pytesseract
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def preprocess_image(image, resize_percent=100, blur_amount=0, threshold_type='none', 
                    denoise=False, contrast_enhance=False, morphology=None):
    """
    Enhanced preprocessing for handwritten Hindi text recognition
    
    Parameters:
    - image: Input image (numpy array)
    - resize_percent: Percentage to resize the image (default: 100%)
    - blur_amount: Amount of Gaussian blur to apply (default: 0, no blur)
    - threshold_type: Type of thresholding to apply (none, simple, adaptive, otsu)
    - denoise: Whether to apply denoising (default: False)
    - contrast_enhance: Whether to enhance contrast (default: False)
    - morphology: Morphological operation to apply (None, 'dilate', 'erode', 'open', 'close')
    
    Returns:
    - Preprocessed image
    """
    try:
        # Create a copy of the image to avoid modifying the original
        processed = image.copy()
        
        # Resize the image if needed
        if resize_percent != 100:
            scale_factor = resize_percent / 100.0
            height, width = processed.shape[:2]
            new_height, new_width = int(height * scale_factor), int(width * scale_factor)
            processed = cv2.resize(processed, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Convert to grayscale
        if len(processed.shape) == 3:
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast if requested
        if contrast_enhance:
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            processed = clahe.apply(processed)
        
        # Apply denoising if requested (good for handwritten text)
        if denoise:
            # Non-local means denoising for grayscale image
            processed = cv2.fastNlMeansDenoising(processed, None, 10, 7, 21)
        
        # Apply blurring if requested
        if blur_amount > 0:
            # Ensure blur_amount is odd
            if blur_amount % 2 == 0:
                blur_amount += 1
            processed = cv2.GaussianBlur(processed, (blur_amount, blur_amount), 0)
        
        # Apply thresholding - critical for handwritten text
        if threshold_type == 'simple':
            _, processed = cv2.threshold(processed, 127, 255, cv2.THRESH_BINARY)
        elif threshold_type == 'adaptive':
            # Adaptive thresholding works well for handwritten text with varying illumination
            processed = cv2.adaptiveThreshold(processed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                             cv2.THRESH_BINARY_INV, 11, 2)
        elif threshold_type == 'otsu':
            # Otsu's method automatically determines optimal threshold value
            _, processed = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Apply morphological operations if requested
        if morphology:
            # Create kernel for morphological operations
            kernel = np.ones((2, 2), np.uint8)
            
            if morphology == 'dilate':
                # Dilation: expands white regions, can connect broken strokes in handwriting
                processed = cv2.dilate(processed, kernel, iterations=1)
            elif morphology == 'erode':
                # Erosion: shrinks white regions, can remove small noise
                processed = cv2.erode(processed, kernel, iterations=1)
            elif morphology == 'open':
                # Opening: erosion followed by dilation, removes noise
                processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
            elif morphology == 'close':
                # Closing: dilation followed by erosion, closes small holes in foreground
                processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    except Exception as e:
        logging.error(f"Error preprocessing image: {str(e)}")
        # Return the original image if preprocessing fails
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

def recognize_hindi(image, handwritten=True):
    """
    Recognize Hindi text from the preprocessed image with enhanced options for handwritten text
    
    Parameters:
    - image: Preprocessed image
    - handwritten: Boolean indicating if the text is handwritten (default: True)
    
    Returns:
    - recognized_text: The recognized Hindi text
    - confidence: Confidence score of the recognition
    """
    try:
        # Set Tesseract configuration for Hindi
        # For handwritten text, we use different PSM (Page Segmentation Mode)
        # PSM 6 = Assume a single uniform block of text
        # PSM 8 = Treat the image as a single word
        # PSM 13 = Raw line. Treat the image as a single text line
        
        if handwritten:
            # For handwritten text, PSM 13 often works better
            config = r'--oem 3 --psm 13 -l hin+eng'
        else:
            config = r'--oem 3 --psm 6 -l hin+eng'
        
        # Check if 'devanagari' language data is available for better handwritten recognition
        if os.path.exists('/usr/share/tesseract-ocr/4.00/tessdata/devanagari.traineddata'):
            config = config.replace('hin+eng', 'hin+eng+devanagari')
            
        # Perform OCR
        result = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
        
        # Extract text and confidence
        text_parts = []
        total_conf = 0
        valid_words = 0
        
        for i in range(len(result["text"])):
            # Skip empty strings
            if result["text"][i].strip():
                text_parts.append(result["text"][i])
                total_conf += int(result["conf"][i])
                valid_words += 1
        
        recognized_text = " ".join(text_parts)
        
        # Calculate average confidence
        avg_confidence = total_conf / valid_words if valid_words > 0 else 0
        
        # Handle case where no text is recognized
        if not recognized_text:
            recognized_text = "No text recognized. Try adjusting the preprocessing parameters."
        
        return recognized_text, avg_confidence
    
    except Exception as e:
        logging.error(f"Error during OCR: {str(e)}")
        return f"OCR Error: {str(e)}", 0
