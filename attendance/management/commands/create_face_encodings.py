from django.core.management.base import BaseCommand
from attendance.models import Employee
from attendance.face_recognition_service import face_service
import base64
import os

class Command(BaseCommand):
    help = 'Create face encodings for employees with profile images but no face encodings'

    def add_arguments(self, parser):
        parser.add_argument('--employee-id', type=str, help='Specific employee ID to process')
        parser.add_argument('--all', action='store_true', help='Process all employees without face encodings')

    def handle(self, *args, **options):
        if options['employee_id']:
            self.process_employee(options['employee_id'])
        elif options['all']:
            self.process_all_employees()
        else:
            self.stdout.write('Please specify --employee-id <ID> or --all')

    def process_employee(self, employee_id):
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            self.create_face_encoding(employee)
        except Employee.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Employee {employee_id} not found'))

    def process_all_employees(self):
        employees = Employee.objects.filter(profile_image__isnull=False)
        for employee in employees:
            if not employee.face_encoding:
                self.create_face_encoding(employee)

    def create_face_encoding(self, employee):
        if not employee.profile_image:
            self.stdout.write(self.style.WARNING(f'No profile image for {employee.employee_id}'))
            return

        try:
            # Read the existing image file
            with open(employee.profile_image.path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
                image_base64 = f"data:image/jpeg;base64,{img_data}"
                
                self.stdout.write(f'Processing {employee.employee_id} - {employee.first_name} {employee.last_name}...')
                
                # Create face encoding
                success, message = face_service.register_employee_face(employee, image_base64)
                
                if success:
                    self.stdout.write(self.style.SUCCESS(f'✅ {employee.employee_id}: {message}'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ {employee.employee_id}: {message}'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing {employee.employee_id}: {str(e)}'))
