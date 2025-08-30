# Face Recognition Attendance System

A comprehensive employee attendance system using face recognition technology.

## Project Structure

```
fransciAttendance/
├── attendance/               # Django app for attendance functionality
├── attendance_system/        # Django project settings
├── media/                    # Media files (employee photos)
│   └── employee_photos/
├── mobile/                   # React Native mobile app
├── scripts/                  # Utility scripts
├── static/                   # Static files
├── venv/                     # Python virtual environment
├── db.sqlite3                # SQLite database
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Tech Stack

**Backend:**
- Python 3.11
- Django 4.2.7
- OpenCV 4.6.0.66 (for face detection)
- SQLite Database
- Django REST Framework (for API endpoints)
- Channels (for WebSocket support)
- Redis (for channel layer)

**Frontend (Mobile):**
- React Native
- Expo
- react-native-vision-camera

## Features

### Core Features
- Employee registration with face encoding
- Face recognition-based attendance (check-in/check-out)
- Real-time attendance tracking
- Daily attendance summaries
- Admin dashboard
- REST API for mobile app integration
- WebSocket for real-time updates

### Future Features
- Shift management
- Leave management
- Payroll integration
- Notification system

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js and npm (for mobile app)
- Redis server (for WebSocket support)

### Backend Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database:**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser (admin):**
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
