import axios from 'axios';

// Configure your Django backend URL
const BASE_URL = 'http://192.168.1.100:8000/api'; // Replace with your actual IP

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const endpoints = {
  employees: '/employees/',
  employeeDetail: (id) => `/employees/${id}/`,
  registerFace: (employeeId) => `/employees/${employeeId}/register-face/`,
  faceRecognitionAttendance: '/attendance/face-recognition/',
  attendanceRecords: '/attendance/records/',
  attendanceSummaries: '/attendance/summaries/',
  employeeAttendanceToday: (employeeId) => `/employees/${employeeId}/attendance/today/`,
};

// API functions
export const apiService = {
  // Employee management
  getEmployees: () => api.get(endpoints.employees),
  createEmployee: (data) => api.post(endpoints.employees, data),
  getEmployee: (id) => api.get(endpoints.employeeDetail(id)),
  updateEmployee: (id, data) => api.put(endpoints.employeeDetail(id), data),
  deleteEmployee: (id) => api.delete(endpoints.employeeDetail(id)),
  
  // Face registration
  registerEmployeeFace: (employeeId, imageBase64) => 
    api.post(endpoints.registerFace(employeeId), { image_base64: imageBase64 }),
  
  // Attendance
  faceRecognitionAttendance: (imageBase64, attendanceType, location = '') =>
    api.post(endpoints.faceRecognitionAttendance, {
      image_base64: imageBase64,
      attendance_type: attendanceType,
      location: location,
    }),
  
  // Records and summaries
  getAttendanceRecords: (params = {}) => api.get(endpoints.attendanceRecords, { params }),
  getAttendanceSummaries: (params = {}) => api.get(endpoints.attendanceSummaries, { params }),
  getEmployeeAttendanceToday: (employeeId) => api.get(endpoints.employeeAttendanceToday(employeeId)),
};

export default api;
