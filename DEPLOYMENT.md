# Face Recognition Attendance System - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- Node.js 16+ installed
- Expo CLI installed (`npm install -g @expo/cli`)
- Android Studio (for Android development) or Xcode (for iOS development)

## Backend Deployment

### 1. Install Python Dependencies
```bash
cd f:/fransciAttendance
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin User
```bash
python manage.py createsuperuser
```

### 4. Test the Setup
```bash
python test_api.py
```

### 5. Start Development Server
```bash
python manage.py runserver
```

**Backend will be available at:** `http://localhost:8000`
**API endpoints at:** `http://localhost:8000/api/`
**Admin panel at:** `http://localhost:8000/admin/`

## Mobile App Deployment

### 1. Install Dependencies
```bash
cd mobile
npm install
```

### 2. Configure API URL
Edit `src/config/api.js` and update the BASE_URL:
```javascript
const BASE_URL = 'http://YOUR_IP_ADDRESS:8000/api';
```

Replace `YOUR_IP_ADDRESS` with your computer's IP address (not localhost).

### 3. Start Expo Development Server
```bash
expo start
```

### 4. Run on Device
- **Android**: Install Expo Go app, scan QR code
- **iOS**: Install Expo Go app, scan QR code
- **Simulator**: Press 'a' for Android or 'i' for iOS

## 📱 API Endpoints Reference

### Employee Management
- `GET /api/employees/` - List all employees
- `POST /api/employees/` - Create new employee
- `GET /api/employees/{id}/` - Get employee details
- `PUT /api/employees/{id}/` - Update employee
- `DELETE /api/employees/{id}/` - Delete employee
- `POST /api/employees/{employee_id}/register-face/` - Register face

### Attendance
- `POST /api/attendance/face-recognition/` - Face recognition attendance
- `GET /api/attendance/records/` - Get attendance records
- `GET /api/attendance/summaries/` - Get daily summaries
- `GET /api/employees/{employee_id}/attendance/today/` - Today's attendance

## 🔧 Configuration

### Django Settings
Key settings in `attendance_system/settings.py`:
- `DEBUG = True` (set to False in production)
- `ALLOWED_HOSTS = []` (add your domain in production)
- `CORS_ALLOW_ALL_ORIGINS = True` (configure properly in production)

### Face Recognition Settings
- **Tolerance**: 0.6 (adjustable in face_recognition_service.py)
- **Confidence threshold**: 60%
- **Image format**: JPEG/PNG with base64 encoding

## 📊 Usage Workflow

### 1. Register Employees
1. Open mobile app
2. Go to "Employees" tab
3. Tap "+" to add new employee
4. Fill employee details
5. Take photo for face recognition
6. Save employee

### 2. Attendance Check-in/out
1. Go to "Attendance" tab
2. Tap "CHECK IN" or "CHECK OUT"
3. Position face in camera
4. Take photo
5. System recognizes face and logs attendance

### 3. View Reports
1. Go to "History" tab
2. Switch between "Records" and "Daily Summary"
3. View attendance data and statistics

## 🛠️ Troubleshooting

### Common Issues

**1. Face Recognition Not Working**
- Ensure good lighting
- Face should be clearly visible
- Only one face in the image
- Employee face must be registered first

**2. API Connection Issues**
- Check if Django server is running
- Verify IP address in mobile app config
- Ensure both devices are on same network
- Check firewall settings

**3. Camera Permissions**
- Grant camera permissions to Expo Go app
- Restart app after granting permissions

**4. Database Issues**
- Run migrations: `python manage.py migrate`
- Check for migration conflicts
- Reset database if needed: delete `db.sqlite3` and re-migrate

## 🔒 Security Considerations

### Development
- CORS is open for development
- Debug mode is enabled
- SQLite database (single file)

### Production Recommendations
- Set `DEBUG = False`
- Configure proper `ALLOWED_HOSTS`
- Use PostgreSQL database
- Implement proper CORS policy
- Add authentication/authorization
- Use HTTPS
- Secure face encoding storage

## 📈 Performance Optimization

### Backend
- Use database indexing for frequent queries
- Implement caching for face encodings
- Optimize image processing
- Use connection pooling

### Mobile
- Implement image compression
- Add offline capability
- Cache API responses
- Optimize bundle size

## 🔄 Future Enhancements

### Planned Features
- Shift management
- Leave management
- Payroll integration
- Push notifications
- Real-time dashboard
- Biometric alternatives
- Multi-location support

### Technical Improvements
- WebSocket for real-time updates
- Background sync
- Advanced analytics
- Machine learning improvements
- Cloud storage integration
