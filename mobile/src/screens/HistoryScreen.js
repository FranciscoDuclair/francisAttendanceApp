import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { apiService } from '../config/api';

export default function HistoryScreen() {
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [summaries, setSummaries] = useState([]);
  const [activeTab, setActiveTab] = useState('records');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    try {
      if (activeTab === 'records') {
        const response = await apiService.getAttendanceRecords();
        setAttendanceRecords(response.data.results || response.data);
      } else {
        const response = await apiService.getAttendanceSummaries();
        setSummaries(response.data.results || response.data);
      }
    } catch (error) {
      console.error('Error loading data:', error);
      Alert.alert('Error', 'Failed to load attendance data');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'N/A';
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const RecordCard = ({ record }) => (
    <View style={styles.recordCard}>
      <View style={styles.recordHeader}>
        <View style={styles.employeeInfo}>
          <Text style={styles.employeeName}>{record.employee_name}</Text>
          <Text style={styles.employeeId}>ID: {record.employee_id}</Text>
        </View>
        <View style={[
          styles.typeBadge,
          { backgroundColor: record.attendance_type === 'check_in' ? '#4CAF50' : '#FF5722' }
        ]}>
          <Ionicons 
            name={record.attendance_type === 'check_in' ? 'log-in' : 'log-out'} 
            size={16} 
            color="white" 
          />
          <Text style={styles.typeText}>
            {record.attendance_type === 'check_in' ? 'IN' : 'OUT'}
          </Text>
        </View>
      </View>
      
      <View style={styles.recordDetails}>
        <View style={styles.detailRow}>
          <Ionicons name="time" size={16} color="#666" />
          <Text style={styles.detailText}>
            {formatDate(record.date)} at {formatTime(record.timestamp)}
          </Text>
        </View>
        
        {record.location && (
          <View style={styles.detailRow}>
            <Ionicons name="location" size={16} color="#666" />
            <Text style={styles.detailText}>{record.location}</Text>
          </View>
        )}
        
        <View style={styles.detailRow}>
          <Ionicons name="analytics" size={16} color="#666" />
          <Text style={styles.detailText}>
            Confidence: {record.confidence_score.toFixed(1)}%
          </Text>
        </View>
      </View>
    </View>
  );

  const SummaryCard = ({ summary }) => (
    <View style={styles.summaryCard}>
      <View style={styles.summaryHeader}>
        <View style={styles.employeeInfo}>
          <Text style={styles.employeeName}>{summary.employee_name}</Text>
          <Text style={styles.employeeId}>ID: {summary.employee_id}</Text>
        </View>
        <View style={styles.statusBadges}>
          <View style={[
            styles.statusBadge,
            { backgroundColor: summary.is_present ? '#4CAF50' : '#F44336' }
          ]}>
            <Text style={styles.statusText}>
              {summary.is_present ? 'Present' : 'Absent'}
            </Text>
          </View>
          {summary.is_late && (
            <View style={[styles.statusBadge, { backgroundColor: '#FF9800' }]}>
              <Text style={styles.statusText}>Late</Text>
            </View>
          )}
        </View>
      </View>
      
      <View style={styles.summaryDetails}>
        <Text style={styles.summaryDate}>{formatDate(summary.date)}</Text>
        
        <View style={styles.timeRow}>
          <View style={styles.timeItem}>
            <Text style={styles.timeLabel}>Check In</Text>
            <Text style={styles.timeValue}>
              {formatTime(summary.check_in_time)}
            </Text>
          </View>
          
          <View style={styles.timeItem}>
            <Text style={styles.timeLabel}>Check Out</Text>
            <Text style={styles.timeValue}>
              {formatTime(summary.check_out_time)}
            </Text>
          </View>
          
          <View style={styles.timeItem}>
            <Text style={styles.timeLabel}>Total Hours</Text>
            <Text style={styles.timeValue}>
              {summary.total_hours || '0.00'}h
            </Text>
          </View>
        </View>
      </View>
    </View>
  );

  const TabButton = ({ title, isActive, onPress }) => (
    <TouchableOpacity
      style={[styles.tabButton, isActive && styles.activeTab]}
      onPress={onPress}
    >
      <Text style={[styles.tabText, isActive && styles.activeTabText]}>
        {title}
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Attendance History</Text>
      </View>

      <View style={styles.tabContainer}>
        <TabButton
          title="Records"
          isActive={activeTab === 'records'}
          onPress={() => setActiveTab('records')}
        />
        <TabButton
          title="Daily Summary"
          isActive={activeTab === 'summaries'}
          onPress={() => setActiveTab('summaries')}
        />
      </View>

      {loading ? (
        <View style={styles.centerContainer}>
          <Text>Loading...</Text>
        </View>
      ) : (
        <FlatList
          data={activeTab === 'records' ? attendanceRecords : summaries}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => 
            activeTab === 'records' ? 
            <RecordCard record={item} /> : 
            <SummaryCard summary={item} />
          }
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          contentContainerStyle={styles.listContainer}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons 
                name={activeTab === 'records' ? 'time-outline' : 'calendar-outline'} 
                size={80} 
                color="#ccc" 
              />
              <Text style={styles.emptyTitle}>No Data Found</Text>
              <Text style={styles.emptySubtitle}>
                {activeTab === 'records' 
                  ? 'No attendance records available' 
                  : 'No daily summaries available'
                }
              </Text>
            </View>
          }
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
    backgroundColor: '#2196F3',
    padding: 20,
    paddingTop: 50,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: 'white',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.18,
    shadowRadius: 1.0,
  },
  tabButton: {
    flex: 1,
    paddingVertical: 15,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#2196F3',
  },
  tabText: {
    fontSize: 16,
    color: '#666',
    fontWeight: '600',
  },
  activeTabText: {
    color: '#2196F3',
  },
  listContainer: {
    padding: 15,
  },
  recordCard: {
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
  recordHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  employeeInfo: {
    flex: 1,
  },
  employeeName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  employeeId: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  typeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
  },
  typeText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
    marginLeft: 5,
  },
  recordDetails: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 10,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  detailText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 10,
  },
  summaryCard: {
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
  summaryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  statusBadges: {
    flexDirection: 'row',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginLeft: 5,
  },
  statusText: {
    color: 'white',
    fontSize: 10,
    fontWeight: '600',
  },
  summaryDetails: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 15,
  },
  summaryDate: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 15,
    textAlign: 'center',
  },
  timeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  timeItem: {
    alignItems: 'center',
    flex: 1,
  },
  timeLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  timeValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
    marginTop: 100,
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
  },
});
