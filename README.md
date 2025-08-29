# Face Recognition Attendance System

A comprehensive employee attendance system using face recognition technology.

## Tech Stack

**Backend:**
- Django 4.2.7
- Django REST Framework
- SQLite Database
- face_recognition library (dlib-based)
- Pillow for image processing

**Frontend:**
- React Native
- Expo (for easier development)
- react-native-vision-camera for camera access

## Features

### Current (Phase 1)
- ✅ Employee registration with face encoding
- ✅ Face recognition-based attendance (check-in/check-out)
- ✅ Attendance records and daily summaries
- ✅ REST API endpoints
- ✅ Admin panel for management

### Future Phases
- Shift management
- Leave management
- Payroll management
- Notification management

## Setup Instructions

### Backend Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

4. **Start Development Server:**
   ```bash
   python manage.py runserver
   ```

### API Endpoints

**Employee Management:**
- `GET/POST /api/employees/` - List/Create employees
- `GET/PUT/DELETE /api/employees/{id}/` - Employee details
- `POST /api/employees/{employee_id}/register-face/` - Register face encoding

**Attendance:**
- `POST /api/attendance/face-recognition/` - Face recognition attendance
- `GET /api/attendance/records/` - Attendance records
- `GET /api/attendance/summaries/` - Daily summaries
- `GET /api/employees/{employee_id}/attendance/today/` - Today's attendance

### Face Recognition API Usage

**Register Employee Face:**
```json
POST /api/employees/EMP001/register-face/
{
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**Attendance Check-in/out:**
```json
POST /api/attendance/face-recognition/
{
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "attendance_type": "check_in",
    "location": "Main Office"
}
```

## Database Schema

### Employee Model
- employee_id (unique)
- Personal info (name, email, phone)
- Work info (department, position, hire_date)
- face_encoding (JSON stored face features)
- profile_image

### AttendanceRecord Model
- employee (foreign key)
- attendance_type (check_in/check_out)
- timestamp, date
- confidence_score
- location, notes

### AttendanceSummary Model
- employee (foreign key)
- date
- check_in_time, check_out_time
- total_hours, is_present, is_late

## Development Notes

- Face recognition uses dlib's ResNet model (99.38% accuracy)
- Images are processed as base64 strings
- Confidence threshold: 60% (adjustable)
- SQLite for development, easily upgradeable to PostgreSQL
- CORS enabled for React Native development
# francisAttendanceApp
