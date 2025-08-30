import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  RefreshControl,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { apiService } from '../config/api';

export default function HomeScreen({ navigation }) {
  const [stats, setStats] = useState({
    totalEmployees: 0,
    presentToday: 0,
    totalRecords: 0,
  });
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [employeesRes, recordsRes, summariesRes] = await Promise.all([
        apiService.getEmployees(),
        apiService.getAttendanceRecords({ date: new Date().toISOString().split('T')[0] }),
        apiService.getAttendanceSummaries({ date: new Date().toISOString().split('T')[0] }),
      ]);

      setStats({
        totalEmployees: employeesRes.data.results?.length || employeesRes.data.length || 0,
        totalRecords: recordsRes.data.results?.length || recordsRes.data.length || 0,
        presentToday: summariesRes.data.results?.filter(s => s.is_present).length || 0,
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadStats();
    setRefreshing(false);
  };

  const StatCard = ({ title, value, icon, color, onPress }) => (
    <TouchableOpacity style={styles.statCard} onPress={onPress}>
      <LinearGradient
        colors={[color, color + '80']}
        style={styles.statGradient}
      >
        <Ionicons name={icon} size={30} color="white" />
        <Text style={styles.statValue}>{value}</Text>
        <Text style={styles.statTitle}>{title}</Text>
      </LinearGradient>
    </TouchableOpacity>
  );

  const QuickAction = ({ title, icon, onPress, color }) => (
    <TouchableOpacity style={styles.actionButton} onPress={onPress}>
      <View style={[styles.actionIcon, { backgroundColor: color }]}>
        <Ionicons name={icon} size={24} color="white" />
      </View>
      <Text style={styles.actionText}>{title}</Text>
    </TouchableOpacity>
  );

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <LinearGradient
        colors={['#2196F3', '#21CBF3']}
        style={styles.header}
      >
        <Text style={styles.headerTitle}>Face Recognition</Text>
        <Text style={styles.headerSubtitle}>Attendance System</Text>
      </LinearGradient>

      <View style={styles.statsContainer}>
        <StatCard
          title="Total Employees"
          value={stats.totalEmployees}
          icon="people"
          color="#4CAF50"
          onPress={() => navigation.navigate('Employees')}
        />
        <StatCard
          title="Present Today"
          value={stats.presentToday}
          icon="checkmark-circle"
          color="#FF9800"
          onPress={() => navigation.navigate('History')}
        />
        <StatCard
          title="Today's Records"
          value={stats.totalRecords}
          icon="time"
          color="#9C27B0"
          onPress={() => navigation.navigate('History')}
        />
      </View>

      <View style={styles.actionsContainer}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        
        <View style={styles.actionsGrid}>
          <QuickAction
            title="Check In/Out"
            icon="camera"
            color="#2196F3"
            onPress={() => navigation.navigate('Attendance')}
          />
          <QuickAction
            title="Register Employee"
            icon="person-add"
            color="#4CAF50"
            onPress={() => navigation.navigate('Employees', { screen: 'RegisterEmployee' })}
          />
          <QuickAction
            title="View History"
            icon="list"
            color="#FF9800"
            onPress={() => navigation.navigate('History')}
          />
          <QuickAction
            title="Manage Employees"
            icon="people"
            color="#9C27B0"
            onPress={() => navigation.navigate('Employees')}
          />
        </View>
      </View>

      <View style={styles.infoContainer}>
        <Text style={styles.infoTitle}>How it works</Text>
        <View style={styles.infoStep}>
          <Ionicons name="person-add" size={20} color="#2196F3" />
          <Text style={styles.infoText}>1. Register employees with their photos</Text>
        </View>
        <View style={styles.infoStep}>
          <Ionicons name="camera" size={20} color="#2196F3" />
          <Text style={styles.infoText}>2. Use camera for face recognition attendance</Text>
        </View>
        <View style={styles.infoStep}>
          <Ionicons name="checkmark-circle" size={20} color="#2196F3" />
          <Text style={styles.infoText}>3. Automatic check-in/out tracking</Text>
        </View>
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
    padding: 40,
    paddingTop: 60,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'white',
    opacity: 0.9,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginTop: -30,
  },
  statCard: {
    flex: 1,
    marginHorizontal: 5,
    borderRadius: 15,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  statGradient: {
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginTop: 10,
  },
  statTitle: {
    fontSize: 12,
    color: 'white',
    textAlign: 'center',
    marginTop: 5,
  },
  actionsContainer: {
    padding: 20,
    marginTop: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    width: '48%',
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    alignItems: 'center',
    marginBottom: 15,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
  },
  actionIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  actionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
  },
  infoContainer: {
    margin: 20,
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.18,
    shadowRadius: 1.0,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  infoStep: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 15,
    flex: 1,
  },
});
