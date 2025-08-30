import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Image,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { takePhoto } from '../utils/imageUtils';
import { apiService } from '../config/api';

export default function AttendanceScreen() {
  const [loading, setLoading] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [lastAttendance, setLastAttendance] = useState(null);

  const handleAttendance = async (type) => {
    if (loading) return;

    setLoading(true);
    try {
      // Take photo
      const photo = await takePhoto();
      if (!photo) {
        setLoading(false);
        return;
      }

      setCapturedImage(photo.uri);

      // Send to API for face recognition
      const response = await apiService.faceRecognitionAttendance(
        photo.base64,
        type,
        'Mobile App'
      );

      const { employee, confidence_score, message } = response.data;

      Alert.alert(
        'Success!',
        `${message}\n\nEmployee: ${employee.name}\nConfidence: ${confidence_score.toFixed(1)}%`,
        [
          {
            text: 'OK',
            onPress: () => {
              setCapturedImage(null);
              setLastAttendance({
                employee: employee.name,
                type: type.replace('_', ' ').toUpperCase(),
                time: new Date().toLocaleTimeString(),
                confidence: confidence_score,
              });
            },
          },
        ]
      );
    } catch (error) {
      console.error('Attendance error:', error);
      setCapturedImage(null);
      
      let errorMessage = 'Failed to process attendance';
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message) {
        errorMessage = error.message;
      }

      Alert.alert('Error', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const AttendanceButton = ({ type, title, icon, color, description }) => (
    <TouchableOpacity
      style={styles.attendanceButton}
      onPress={() => handleAttendance(type)}
      disabled={loading}
    >
      <LinearGradient
        colors={[color, color + '80']}
        style={styles.buttonGradient}
      >
        <Ionicons name={icon} size={40} color="white" />
        <Text style={styles.buttonTitle}>{title}</Text>
        <Text style={styles.buttonDescription}>{description}</Text>
      </LinearGradient>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#2196F3', '#21CBF3']}
        style={styles.header}
      >
        <Ionicons name="camera" size={50} color="white" />
        <Text style={styles.headerTitle}>Face Recognition</Text>
        <Text style={styles.headerSubtitle}>Attendance System</Text>
      </LinearGradient>

      <View style={styles.content}>
        {capturedImage && (
          <View style={styles.imageContainer}>
            <Image source={{ uri: capturedImage }} style={styles.capturedImage} />
            <Text style={styles.processingText}>Processing...</Text>
          </View>
        )}

        {lastAttendance && !capturedImage && (
          <View style={styles.lastAttendanceContainer}>
            <Ionicons name="checkmark-circle" size={30} color="#4CAF50" />
            <Text style={styles.lastAttendanceTitle}>Last Attendance</Text>
            <Text style={styles.lastAttendanceEmployee}>{lastAttendance.employee}</Text>
            <Text style={styles.lastAttendanceDetails}>
              {lastAttendance.type} at {lastAttendance.time}
            </Text>
            <Text style={styles.lastAttendanceConfidence}>
              Confidence: {lastAttendance.confidence.toFixed(1)}%
            </Text>
          </View>
        )}

        <View style={styles.instructionsContainer}>
          <Text style={styles.instructionsTitle}>Instructions</Text>
          <View style={styles.instructionItem}>
            <Ionicons name="person" size={20} color="#2196F3" />
            <Text style={styles.instructionText}>Position your face in the camera</Text>
          </View>
          <View style={styles.instructionItem}>
            <Ionicons name="sunny" size={20} color="#2196F3" />
            <Text style={styles.instructionText}>Ensure good lighting</Text>
          </View>
          <View style={styles.instructionItem}>
            <Ionicons name="eye" size={20} color="#2196F3" />
            <Text style={styles.instructionText}>Look directly at the camera</Text>
          </View>
        </View>

        <View style={styles.buttonsContainer}>
          <AttendanceButton
            type="check_in"
            title="CHECK IN"
            icon="log-in"
            color="#4CAF50"
            description="Start your work day"
          />
          
          <AttendanceButton
            type="check_out"
            title="CHECK OUT"
            icon="log-out"
            color="#FF5722"
            description="End your work day"
          />
        </View>

        {loading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color="#2196F3" />
            <Text style={styles.loadingText}>Processing face recognition...</Text>
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 40,
    paddingTop: 60,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginTop: 10,
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'white',
    opacity: 0.9,
    marginTop: 5,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  capturedImage: {
    width: 150,
    height: 150,
    borderRadius: 75,
    borderWidth: 3,
    borderColor: '#2196F3',
  },
  processingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#2196F3',
    fontWeight: '600',
  },
  lastAttendanceContainer: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    alignItems: 'center',
    marginBottom: 20,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
  },
  lastAttendanceTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 10,
  },
  lastAttendanceEmployee: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2196F3',
    marginTop: 5,
  },
  lastAttendanceDetails: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  lastAttendanceConfidence: {
    fontSize: 12,
    color: '#4CAF50',
    marginTop: 5,
  },
  instructionsContainer: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.18,
    shadowRadius: 1.0,
  },
  instructionsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  instructionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  instructionText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 15,
    flex: 1,
  },
  buttonsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  attendanceButton: {
    flex: 1,
    marginHorizontal: 10,
    borderRadius: 15,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  buttonGradient: {
    padding: 25,
    borderRadius: 15,
    alignItems: 'center',
  },
  buttonTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    marginTop: 10,
  },
  buttonDescription: {
    fontSize: 12,
    color: 'white',
    opacity: 0.9,
    marginTop: 5,
    textAlign: 'center',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: '#2196F3',
    fontWeight: '600',
  },
});
