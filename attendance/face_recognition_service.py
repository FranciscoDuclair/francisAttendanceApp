import cv2
import numpy as np
from PIL import Image
import base64
import io
from django.core.files.base import ContentFile
from .models import Employee


class FaceRecognitionService:
    
    def __init__(self):
        # Initialize face detection cascade
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except (AttributeError, TypeError):
            # Fallback for opencv-python-headless or missing cascade
            import os
            try:
                if hasattr(cv2, '__file__') and cv2.__file__:
                    cascade_path = os.path.join(os.path.dirname(cv2.__file__), 'data', 'haarcascade_frontalface_default.xml')
                    if os.path.exists(cascade_path):
                        self.face_cascade = cv2.CascadeClassifier(cascade_path)
                    else:
                        self.face_cascade = None
                else:
                    self.face_cascade = None
            except:
                self.face_cascade = None
            
            if self.face_cascade is None:
                print("Warning: Face cascade not available. Face detection may not work properly.")
        # Initialize face recognizer
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.is_trained = False
        self.employee_map = {}
        
    def detect_faces(self, image):
        """
        Detect faces in an image using the cascade classifier
        Args:
            image: numpy array of the image in BGR format
        Returns:
            List of rectangles (x, y, w, h) containing the faces
        """
        if self.face_cascade is None:
            raise ValueError("Face cascade classifier not initialized")
            
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces
    
    def encode_face_from_base64(self, image_base64):
        """
        Extract face encoding from base64 image string using OpenCV
        Returns: face encoding array or None if no face found
        """
        try:
            # Decode base64 image
            format, imgstr = image_base64.split(';base64,')
            image_data = base64.b64decode(imgstr)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert PIL image to numpy array
            image_array = np.array(image)
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Detect faces
            faces = self.detect_faces(image_array)
            
            if len(faces) == 0:
                return None, "No face detected in the image"
            
            if len(faces) > 1:
                return None, "Multiple faces detected. Please ensure only one face is visible"
            
            # Extract face region
            (x, y, w, h) = faces[0]
            face_region = gray[y:y+h, x:x+w]
            
            # Resize to standard size
            face_resized = cv2.resize(face_region, (100, 100))
            
            return face_resized, "Face encoded successfully"
                
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
    
    def train_recognizer(self):
        """Train the face recognizer with all registered employees"""
        try:
            faces = []
            labels = []
            self.employee_map = {}
            
            employees = Employee.objects.filter(face_encoding__isnull=False, is_active=True)
            
            for idx, employee in enumerate(employees):
                face_data = employee.get_face_encoding()
                if face_data is not None:
                    faces.append(np.array(face_data, dtype=np.uint8))
                    labels.append(idx)
                    self.employee_map[idx] = employee
            
            if len(faces) > 0:
                self.face_recognizer.train(faces, np.array(labels))
                self.is_trained = True
                return True, f"Trained with {len(faces)} employees"
            else:
                return False, "No employee faces found for training"
                
        except Exception as e:
            return False, f"Training failed: {str(e)}"
    
    def recognize_face(self, image_base64, confidence_threshold=50):
        """
        Recognize face from base64 image against all registered employees using OpenCV
        Returns: (employee, confidence_score) or (None, error_message)
        """
        try:
            # Get face encoding from uploaded image
            face_encoding, message = self.encode_face_from_base64(image_base64)
            
            if face_encoding is None:
                return None, 0.0, message
            
            # Train recognizer if not already trained
            if not self.is_trained:
                success, train_message = self.train_recognizer()
                if not success:
                    return None, 0.0, train_message
            
            # Predict using the trained recognizer
            label, confidence = self.face_recognizer.predict(face_encoding)
            
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
        """
        Register face encoding for an employee
        Returns: success boolean and message
        """
        try:
            face_encoding, message = self.encode_face_from_base64(image_base64)
            
            if face_encoding is None:
                return False, message
            
            # Store face encoding
            employee.set_face_encoding(face_encoding)
            employee.save()
            
            return True, "Face registered successfully"
            
        except Exception as e:
            return False, f"Error registering face: {str(e)}"
    
    def update_employee_face(self, employee, image_base64):
        """
        Update face encoding for an existing employee
        Returns: success boolean and message
        """
        return self.register_employee_face(employee, image_base64)


# Global instance
face_service = FaceRecognitionService()
