import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { apiService } from '../config/api';

export default function EmployeeScreen({ navigation }) {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    try {
      const response = await apiService.getEmployees();
      setEmployees(response.data.results || response.data);
    } catch (error) {
      console.error('Error loading employees:', error);
      Alert.alert('Error', 'Failed to load employees');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadEmployees();
    setRefreshing(false);
  };

  const deleteEmployee = async (employee) => {
    Alert.alert(
      'Delete Employee',
      `Are you sure you want to delete ${employee.first_name} ${employee.last_name}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await apiService.deleteEmployee(employee.id);
              loadEmployees();
              Alert.alert('Success', 'Employee deleted successfully');
            } catch (error) {
              Alert.alert('Error', 'Failed to delete employee');
            }
          },
        },
      ]
    );
  };

  const EmployeeCard = ({ employee }) => (
    <TouchableOpacity style={styles.employeeCard}>
      <View style={styles.employeeInfo}>
        <View style={styles.avatarContainer}>
          {employee.profile_image ? (
            <Image source={{ uri: employee.profile_image }} style={styles.avatar} />
          ) : (
            <View style={styles.avatarPlaceholder}>
              <Ionicons name="person" size={30} color="#666" />
            </View>
          )}
          {employee.face_encoding && (
            <View style={styles.faceRegisteredBadge}>
              <Ionicons name="checkmark" size={12} color="white" />
            </View>
          )}
        </View>
        
        <View style={styles.employeeDetails}>
          <Text style={styles.employeeName}>
            {employee.first_name} {employee.last_name}
          </Text>
          <Text style={styles.employeeId}>ID: {employee.employee_id}</Text>
          <Text style={styles.employeeDepartment}>{employee.department}</Text>
          <Text style={styles.employeePosition}>{employee.position}</Text>
        </View>
      </View>

      <View style={styles.employeeActions}>
        <TouchableOpacity
          style={[styles.actionButton, styles.editButton]}
          onPress={() => navigation.navigate('RegisterEmployee', { employee })}
        >
          <Ionicons name="create" size={20} color="white" />
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.actionButton, styles.deleteButton]}
          onPress={() => deleteEmployee(employee)}
        >
          <Ionicons name="trash" size={20} color="white" />
        </TouchableOpacity>
      </View>

      <View style={styles.statusContainer}>
        <View style={[
          styles.statusBadge,
          { backgroundColor: employee.is_active ? '#4CAF50' : '#F44336' }
        ]}>
          <Text style={styles.statusText}>
            {employee.is_active ? 'Active' : 'Inactive'}
          </Text>
        </View>
        
        {employee.face_encoding && (
          <View style={styles.faceStatusBadge}>
            <Ionicons name="face-recognition" size={12} color="#2196F3" />
            <Text style={styles.faceStatusText}>Face Registered</Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <Text>Loading employees...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Employees</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => navigation.navigate('RegisterEmployee')}
        >
          <Ionicons name="add" size={24} color="white" />
        </TouchableOpacity>
      </View>

      {employees.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="people-outline" size={80} color="#ccc" />
          <Text style={styles.emptyTitle}>No Employees Found</Text>
          <Text style={styles.emptySubtitle}>
            Add your first employee to get started
          </Text>
          <TouchableOpacity
            style={styles.emptyButton}
            onPress={() => navigation.navigate('RegisterEmployee')}
          >
            <Text style={styles.emptyButtonText}>Add Employee</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={employees}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => <EmployeeCard employee={item} />}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          contentContainerStyle={styles.listContainer}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#2196F3',
    padding: 20,
    paddingTop: 50,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  addButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 25,
    width: 50,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContainer: {
    padding: 15,
  },
  employeeCard: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 15,
    marginBottom: 15,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
  },
  employeeInfo: {
    flexDirection: 'row',
    marginBottom: 10,
  },
  avatarContainer: {
    position: 'relative',
    marginRight: 15,
  },
  avatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
  },
  avatarPlaceholder: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  faceRegisteredBadge: {
    position: 'absolute',
    bottom: -2,
    right: -2,
    backgroundColor: '#4CAF50',
    borderRadius: 10,
    width: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  employeeDetails: {
    flex: 1,
  },
  employeeName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 2,
  },
  employeeId: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  employeeDepartment: {
    fontSize: 14,
    color: '#2196F3',
    marginBottom: 2,
  },
  employeePosition: {
    fontSize: 12,
    color: '#999',
  },
  employeeActions: {
    flexDirection: 'row',
    position: 'absolute',
    top: 15,
    right: 15,
  },
  actionButton: {
    width: 35,
    height: 35,
    borderRadius: 17.5,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 10,
  },
  editButton: {
    backgroundColor: '#FF9800',
  },
  deleteButton: {
    backgroundColor: '#F44336',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 10,
  },
  statusText: {
    fontSize: 12,
    color: 'white',
    fontWeight: '600',
  },
  faceStatusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  faceStatusText: {
    fontSize: 10,
    color: '#2196F3',
    marginLeft: 4,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
    marginBottom: 10,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  emptyButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  emptyButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
