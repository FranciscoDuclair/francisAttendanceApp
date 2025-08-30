#!/usr/bin/env python3
"""
Setup script for Face Recognition Attendance System
"""
import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def setup_django():
    """Setup Django backend"""
    print("🚀 Setting up Django Backend...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
    
    # Setup Django
    django.setup()
    
    # Run migrations
    print("\n📦 Creating database migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    print("\n🗄️ Applying database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("\n✅ Django backend setup completed!")
    return True

def create_sample_data():
    """Create sample employee data"""
    print("\n👥 Creating sample employee data...")
    
    from attendance.models import Employee
    from datetime import date
    
    # Create sample employee
    if not Employee.objects.filter(employee_id='EMP001').exists():
        employee = Employee.objects.create(
            employee_id='EMP001',
            first_name='John',
            last_name='Doe',
            email='john.doe@company.com',
            phone='+1234567890',
            department='IT',
            position='Software Developer',
            hire_date=date.today(),
            is_active=True
        )
        print(f"✅ Created sample employee: {employee}")
    else:
        print("ℹ️ Sample employee already exists")

def main():
    """Main setup function"""
    print("🎯 Face Recognition Attendance System Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Setup Django
    if not setup_django():
        print("❌ Django setup failed!")
        sys.exit(1)
    
    # Create sample data
    try:
        create_sample_data()
    except Exception as e:
        print(f"⚠️ Warning: Could not create sample data: {e}")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Create superuser: python manage.py createsuperuser")
    print("3. Start server: python manage.py runserver")
    print("4. Setup mobile app: cd mobile && npm install && expo start")
    print("\nAPI will be available at: http://localhost:8000/api/")
    print("Admin panel at: http://localhost:8000/admin/")

if __name__ == '__main__':
    main()
