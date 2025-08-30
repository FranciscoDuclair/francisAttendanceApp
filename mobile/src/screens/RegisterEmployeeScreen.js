import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  Image,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { takePhoto, pickImage, showImagePickerOptions } from '../utils/imageUtils';
import { apiService } from '../config/api';

export default function RegisterEmployeeScreen({ navigation, route }) {
  const [employee, setEmployee] = useState({
    employee_id: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    department: '',
    position: '',
    hire_date: new Date().toISOString().split('T')[0],
    is_active: true,
  });
  const [profileImage, setProfileImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (route.params?.employee) {
      const emp = route.params.employee;
      setEmployee(emp);
      setIsEditing(true);
      if (emp.profile_image) {
        setProfileImage({ uri: emp.profile_image });
      }
    }
  }, [route.params]);

  const handleImagePicker = async () => {
    const option = await showImagePickerOptions();
    if (!option) return;

    let image;
    if (option === 'camera') {
      image = await takePhoto();
    } else {
      image = await pickImage();
    }

    if (image) {
      setProfileImage(image);
    }
  };

  const validateForm = () => {
    if (!employee.employee_id.trim()) {
      Alert.alert('Error', 'Employee ID is required');
      return false;
    }
    if (!employee.first_name.trim()) {
      Alert.alert('Error', 'First name is required');
      return false;
    }
    if (!employee.last_name.trim()) {
      Alert.alert('Error', 'Last name is required');
      return false;
    }
    if (!employee.email.trim()) {
      Alert.alert('Error', 'Email is required');
      return false;
    }
    if (!employee.email.includes('@')) {
      Alert.alert('Error', 'Please enter a valid email');
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      let employeeData = { ...employee };
      
      // Add profile image if selected
      if (profileImage && profileImage.base64) {
        employeeData.profile_image_base64 = profileImage.base64;
      }

      let response;
      if (isEditing) {
        response = await apiService.updateEmployee(employee.id, employeeData);
      } else {
        response = await apiService.createEmployee(employeeData);
      }

      const savedEmployee = response.data;

      // Register face if image was provided
      if (profileImage && profileImage.base64) {
        try {
          await apiService.registerEmployeeFace(
            savedEmployee.employee_id,
            profileImage.base64
          );
          Alert.alert(
            'Success',
            `Employee ${isEditing ? 'updated' : 'registered'} successfully with face recognition!`,
            [{ text: 'OK', onPress: () => navigation.goBack() }]
          );
        } catch (faceError) {
          Alert.alert(
            'Partial Success',
            `Employee ${isEditing ? 'updated' : 'registered'} successfully, but face registration failed. You can register the face later.`,
            [{ text: 'OK', onPress: () => navigation.goBack() }]
          );
        }
      } else {
        Alert.alert(
          'Success',
          `Employee ${isEditing ? 'updated' : 'registered'} successfully!`,
          [{ text: 'OK', onPress: () => navigation.goBack() }]
        );
      }
    } catch (error) {
      console.error('Error saving employee:', error);
      let errorMessage = `Failed to ${isEditing ? 'update' : 'register'} employee`;
      
      if (error.response?.data) {
        const errors = error.response.data;
        if (typeof errors === 'object') {
          errorMessage = Object.values(errors).flat().join('\n');
        } else {
          errorMessage = errors.toString();
        }
      }
      
      Alert.alert('Error', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={24} color="white" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>
          {isEditing ? 'Edit Employee' : 'Register Employee'}
        </Text>
      </View>

      <View style={styles.content}>
        {/* Profile Image Section */}
        <View style={styles.imageSection}>
          <TouchableOpacity style={styles.imageContainer} onPress={handleImagePicker}>
            {profileImage ? (
              <Image source={{ uri: profileImage.uri }} style={styles.profileImage} />
            ) : (
              <View style={styles.imagePlaceholder}>
                <Ionicons name="camera" size={40} color="#666" />
                <Text style={styles.imagePlaceholderText}>Add Photo</Text>
              </View>
            )}
          </TouchableOpacity>
          <Text style={styles.imageHint}>
            Tap to {profileImage ? 'change' : 'add'} photo for face recognition
          </Text>
        </View>

        {/* Form Fields */}
        <View style={styles.form}>
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Employee ID *</Text>
            <TextInput
              style={styles.input}
              value={employee.employee_id}
              onChangeText={(text) => setEmployee({ ...employee, employee_id: text })}
              placeholder="Enter employee ID"
              editable={!isEditing}
            />
          </View>

          <View style={styles.row}>
            <View style={[styles.inputGroup, styles.halfWidth]}>
              <Text style={styles.label}>First Name *</Text>
              <TextInput
                style={styles.input}
                value={employee.first_name}
                onChangeText={(text) => setEmployee({ ...employee, first_name: text })}
                placeholder="First name"
              />
            </View>

            <View style={[styles.inputGroup, styles.halfWidth]}>
              <Text style={styles.label}>Last Name *</Text>
              <TextInput
                style={styles.input}
                value={employee.last_name}
                onChangeText={(text) => setEmployee({ ...employee, last_name: text })}
                placeholder="Last name"
              />
            </View>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Email *</Text>
            <TextInput
              style={styles.input}
              value={employee.email}
              onChangeText={(text) => setEmployee({ ...employee, email: text })}
              placeholder="Enter email address"
              keyboardType="email-address"
              autoCapitalize="none"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Phone</Text>
            <TextInput
              style={styles.input}
              value={employee.phone}
              onChangeText={(text) => setEmployee({ ...employee, phone: text })}
              placeholder="Enter phone number"
              keyboardType="phone-pad"
            />
          </View>

          <View style={styles.row}>
            <View style={[styles.inputGroup, styles.halfWidth]}>
              <Text style={styles.label}>Department</Text>
              <TextInput
                style={styles.input}
                value={employee.department}
                onChangeText={(text) => setEmployee({ ...employee, department: text })}
                placeholder="Department"
              />
            </View>

            <View style={[styles.inputGroup, styles.halfWidth]}>
              <Text style={styles.label}>Position</Text>
              <TextInput
                style={styles.input}
                value={employee.position}
                onChangeText={(text) => setEmployee({ ...employee, position: text })}
                placeholder="Position"
              />
            </View>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Hire Date</Text>
            <TextInput
              style={styles.input}
              value={employee.hire_date}
              onChangeText={(text) => setEmployee({ ...employee, hire_date: text })}
              placeholder="YYYY-MM-DD"
            />
          </View>

          {/* Status Toggle */}
          <View style={styles.statusContainer}>
            <Text style={styles.label}>Status</Text>
            <TouchableOpacity
              style={[
                styles.statusToggle,
                { backgroundColor: employee.is_active ? '#4CAF50' : '#F44336' }
              ]}
              onPress={() => setEmployee({ ...employee, is_active: !employee.is_active })}
            >
              <Text style={styles.statusText}>
                {employee.is_active ? 'Active' : 'Inactive'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Submit Button */}
        <TouchableOpacity
          style={[styles.submitButton, loading && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <>
              <Ionicons 
                name={isEditing ? "checkmark" : "person-add"} 
                size={20} 
                color="white" 
              />
              <Text style={styles.submitButtonText}>
                {isEditing ? 'Update Employee' : 'Register Employee'}
              </Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#2196F3',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    paddingTop: 50,
  },
  backButton: {
    marginRight: 15,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
  },
  content: {
    padding: 20,
  },
  imageSection: {
    alignItems: 'center',
    marginBottom: 30,
  },
  imageContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    marginBottom: 10,
  },
  profileImage: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 3,
    borderColor: '#2196F3',
  },
  imagePlaceholder: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#f0f0f0',
    borderWidth: 2,
    borderColor: '#ddd',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
  },
  imagePlaceholderText: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  imageHint: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  form: {
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
  inputGroup: {
    marginBottom: 20,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  halfWidth: {
    width: '48%',
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    backgroundColor: '#fafafa',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  statusToggle: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
  },
  statusText: {
    color: 'white',
    fontWeight: '600',
  },
  submitButton: {
    backgroundColor: '#2196F3',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 18,
    borderRadius: 15,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
  },
  submitButtonDisabled: {
    backgroundColor: '#ccc',
  },
  submitButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});
