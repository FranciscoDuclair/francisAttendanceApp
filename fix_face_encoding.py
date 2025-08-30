#!/usr/bin/env python3
"""
Script to manually create face encoding for existing employee
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance.models import Employee
from attendance.face_recognition_service import face_service
import base64

def fix_employee_face_encoding(employee_id):
    """Create face encoding for employee using their existing profile image"""
    try:
        employee = Employee.objects.get(employee_id=employee_id)
        
        if not employee.profile_image:
            print(f"❌ Employee {employee_id} has no profile image")
            return False
        
        # Read the existing image file
        with open(employee.profile_image.path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
            image_base64 = f"data:image/jpeg;base64,{img_data}"
            
            print(f"🔄 Processing face encoding for {employee.first_name} {employee.last_name}...")
            
            # Create face encoding
            success, message = face_service.register_employee_face(employee, image_base64)
            
            if success:
                print(f"✅ Face encoding created successfully: {message}")
                
                # Verify encoding was saved
                employee.refresh_from_db()
                if employee.face_encoding:
                    print(f"✅ Face encoding verified in database")
                    return True
                else:
                    print(f"❌ Face encoding not found in database after creation")
                    return False
            else:
                print(f"❌ Face encoding failed: {message}")
                return False
                
    except Employee.DoesNotExist:
        print(f"❌ Employee {employee_id} not found")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        employee_id = sys.argv[1]
        fix_employee_face_encoding(employee_id)
    else:
        print("Usage: python fix_face_encoding.py <employee_id>")
        print("Example: python fix_face_encoding.py 001")
