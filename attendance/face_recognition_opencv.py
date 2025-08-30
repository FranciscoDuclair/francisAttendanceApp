import cv2
import numpy as np
from PIL import Image
import base64
import io
import os
from django.conf import settings
from .models import Employee

class OpenCVFaceRecognitionService:
    """
    Alternative face recognition service using OpenCV instead of dlib
    This avoids the CMake dependency issue on Windows
    """
    
    def __init__(self):
        # Load OpenCV's pre-trained face detection model
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Initialize face recognizer
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.is_trained = False
        
    @staticmethod
    def decode_base64_image(image_base64):
        """Decode base64 image to numpy array"""
        try:
            format, imgstr = image_base64.split(';base64,')
            image_data = base64.b64decode(imgstr)
            image = Image.open(io.BytesIO(image_data))
            return np.array(image)
        except Exception as e:
            raise ValueError(f"Invalid image format: {str(e)}")
    
    def detect_face(self, image_array):
        """Detect face in image and return face region"""
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return None, "No face detected in the image"
        
        if len(faces) > 1:
            return None, "Multiple faces detected. Please ensure only one face is visible"
        
        # Return the largest face
        (x, y, w, h) = faces[0]
        face_region = gray[y:y+h, x:x+w]
        return face_region, "Face detected successfully"
    
    def extract_face_features(self, image_base64):
        """Extract face features from base64 image"""
        try:
            image_array = self.decode_base64_image(image_base64)
            face_region, message = self.detect_face(image_array)
            
            if face_region is None:
                return None, message
            
            # Resize face to standard size
            face_resized = cv2.resize(face_region, (100, 100))
            return face_resized, "Face features extracted successfully"
            
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
    
    def train_recognizer(self):
        """Train the face recognizer with all registered employees"""
        try:
            faces = []
            labels = []
            employee_map = {}
            
            employees = Employee.objects.filter(face_encoding__isnull=False, is_active=True)
            
            for idx, employee in enumerate(employees):
                face_data = employee.get_face_encoding()
                if face_data is not None:
                    faces.append(face_data)
                    labels.append(idx)
                    employee_map[idx] = employee
            
            if len(faces) > 0:
                self.face_recognizer.train(faces, np.array(labels))
                self.is_trained = True
                self.employee_map = employee_map
                return True, f"Trained with {len(faces)} employees"
            else:
                return False, "No employee faces found for training"
                
        except Exception as e:
            return False, f"Training failed: {str(e)}"
    
    def recognize_face(self, image_base64, confidence_threshold=50):
        """Recognize face from base64 image"""
        try:
            # Extract face features
            face_features, message = self.extract_face_features(image_base64)
            if face_features is None:
                return None, 0.0, message
            
            # Train recognizer if not already trained
            if not self.is_trained:
                success, train_message = self.train_recognizer()
                if not success:
                    return None, 0.0, train_message
            
            # Predict
            label, confidence = self.face_recognizer.predict(face_features)
            
            # Convert confidence to percentage (lower is better for LBPH)
            confidence_score = max(0, 100 - confidence)
            
            if confidence_score >= confidence_threshold and label in self.employee_map:
                employee = self.employee_map[label]
                return employee, confidence_score, "Face recognized successfully"
            else:
                return None, confidence_score, "Face not recognized"
                
        except Exception as e:
            return None, 0.0, f"Error during face recognition: {str(e)}"
    
    def register_employee_face(self, employee, image_base64):
        """Register face for an employee"""
        try:
            face_features, message = self.extract_face_features(image_base64)
            if face_features is None:
                return False, message
            
            # Store face features as JSON
            employee.set_face_encoding(face_features)
            employee.save()
            
            # Retrain the recognizer
            self.train_recognizer()
            
            return True, "Face registered successfully"
            
        except Exception as e:
            return False, f"Error registering face: {str(e)}"


# Global instance
opencv_face_service = OpenCVFaceRecognitionService()
