import * as ImagePicker from 'expo-image-picker';
import { Alert } from 'react-native';

export const requestCameraPermissions = async () => {
  const { status } = await ImagePicker.requestCameraPermissionsAsync();
  if (status !== 'granted') {
    Alert.alert('Permission Required', 'Camera permission is required to take photos for face recognition.');
    return false;
  }
  return true;
};

export const requestMediaLibraryPermissions = async () => {
  const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
  if (status !== 'granted') {
    Alert.alert('Permission Required', 'Media library permission is required to select photos.');
    return false;
  }
  return true;
};

export const takePhoto = async () => {
  const hasPermission = await requestCameraPermissions();
  if (!hasPermission) return null;

  try {
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
      base64: true,
    });

    if (!result.canceled && result.assets[0]) {
      return {
        uri: result.assets[0].uri,
        base64: `data:image/jpeg;base64,${result.assets[0].base64}`,
      };
    }
    return null;
  } catch (error) {
    Alert.alert('Error', 'Failed to take photo: ' + error.message);
    return null;
  }
};

export const pickImage = async () => {
  const hasPermission = await requestMediaLibraryPermissions();
  if (!hasPermission) return null;

  try {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
      base64: true,
    });

    if (!result.canceled && result.assets[0]) {
      return {
        uri: result.assets[0].uri,
        base64: `data:image/jpeg;base64,${result.assets[0].base64}`,
      };
    }
    return null;
  } catch (error) {
    Alert.alert('Error', 'Failed to pick image: ' + error.message);
    return null;
  }
};

export const showImagePickerOptions = () => {
  return new Promise((resolve) => {
    Alert.alert(
      'Select Photo',
      'Choose how you want to add a photo',
      [
        { text: 'Camera', onPress: () => resolve('camera') },
        { text: 'Gallery', onPress: () => resolve('gallery') },
        { text: 'Cancel', onPress: () => resolve(null), style: 'cancel' },
      ]
    );
  });
};
