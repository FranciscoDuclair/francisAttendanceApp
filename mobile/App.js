import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

import HomeScreen from './src/screens/HomeScreen';
import AttendanceScreen from './src/screens/AttendanceScreen';
import EmployeeScreen from './src/screens/EmployeeScreen';
import HistoryScreen from './src/screens/HistoryScreen';
import RegisterEmployeeScreen from './src/screens/RegisterEmployeeScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function EmployeeStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen 
        name="EmployeeList" 
        component={EmployeeScreen} 
        options={{ title: 'Employees' }}
      />
      <Stack.Screen 
        name="RegisterEmployee" 
        component={RegisterEmployeeScreen} 
        options={{ title: 'Register Employee' }}
      />
    </Stack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Attendance') {
            iconName = focused ? 'camera' : 'camera-outline';
          } else if (route.name === 'Employees') {
            iconName = focused ? 'people' : 'people-outline';
          } else if (route.name === 'History') {
            iconName = focused ? 'time' : 'time-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2196F3',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Attendance" component={AttendanceScreen} />
      <Tab.Screen name="Employees" component={EmployeeStack} />
      <Tab.Screen name="History" component={HistoryScreen} />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <MainTabs />
    </NavigationContainer>
  );
}
