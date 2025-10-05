import React, { useState } from 'react';
import {
    Alert,
    KeyboardAvoidingView,
    Platform,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from 'react-native';

interface LoginFormData {
  email: string;
  password: string;
  confirmPassword?: string;
}

const LoginPage: React.FC = () => {
  const [isLoginMode, setIsLoginMode] = useState<boolean>(true);
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showFAQ, setShowFAQ] = useState<boolean>(false);

  const handleInputChange = (field: keyof LoginFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = () => {
    if (!formData.email || !formData.password) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (!isLoginMode && formData.password !== formData.confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    // Here you would typically make an API call
    Alert.alert(
      'Success', 
      `${isLoginMode ? 'Login' : 'Sign up'} successful!`
    );
  };

  const handleForgotPassword = () => {
    if (!formData.email) {
      Alert.alert('Error', 'Please enter your email first');
      return;
    }
    Alert.alert('Password Reset', 'Reset link sent to your email');
  };

  const toggleMode = () => {
    setIsLoginMode(!isLoginMode);
    setFormData({
      email: '',
      password: '',
      confirmPassword: '',
    });
  };

  const faqData = [
    {
      question: "How do I reset my password?",
      answer: "Click 'Forgot Password' and enter your email address. You'll receive a reset link."
    },
    {
      question: "Can I use my social media account?",
      answer: "Currently, we support email/password authentication only."
    },
    {
      question: "Is my data secure?",
      answer: "Yes, we use industry-standard encryption to protect your information."
    },
    {
      question: "How do I create an account?",
      answer: "Click 'Sign Up' and fill in your email and password."
    }
  ];

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingView}
      >
        <ScrollView contentContainerStyle={styles.scrollContainer}>
          <View style={styles.headerContainer}>
            <Text style={styles.title}>
              {isLoginMode ? 'Welcome Back' : 'Create Account'}
            </Text>
            <Text style={styles.subtitle}>
              {isLoginMode 
                ? 'Sign in to your account' 
                : 'Sign up to get started'
              }
            </Text>
          </View>

          <View style={styles.formContainer}>
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Email</Text>
              <TextInput
                style={styles.input}
                placeholder="Enter your email"
                value={formData.email}
                onChangeText={(value) => handleInputChange('email', value)}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Password</Text>
              <TextInput
                style={styles.input}
                placeholder="Enter your password"
                value={formData.password}
                onChangeText={(value) => handleInputChange('password', value)}
                secureTextEntry
                autoCapitalize="none"
              />
            </View>

            {!isLoginMode && (
              <View style={styles.inputContainer}>
                <Text style={styles.inputLabel}>Confirm Password</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChangeText={(value) => handleInputChange('confirmPassword', value)}
                  secureTextEntry
                  autoCapitalize="none"
                />
              </View>
            )}

            {isLoginMode && (
              <TouchableOpacity 
                style={styles.forgotPasswordContainer}
                onPress={handleForgotPassword}
              >
                <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
              </TouchableOpacity>
            )}

            <TouchableOpacity 
              style={styles.loginButton}
              onPress={handleSubmit}
            >
              <Text style={styles.loginButtonText}>
                {isLoginMode ? 'Login' : 'Sign Up'}
              </Text>
            </TouchableOpacity>

            <View style={styles.toggleContainer}>
              <Text style={styles.toggleText}>
                {isLoginMode 
                  ? "Don't have an account? " 
                  : "Already have an account? "
                }
              </Text>
              <TouchableOpacity onPress={toggleMode}>
                <Text style={styles.toggleLink}>
                  {isLoginMode ? 'Sign Up' : 'Login'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.faqContainer}>
            <TouchableOpacity 
              style={styles.faqToggle}
              onPress={() => setShowFAQ(!showFAQ)}
            >
              <Text style={styles.faqToggleText}>
                {showFAQ ? 'Hide' : 'Show'} FAQ
              </Text>
            </TouchableOpacity>

            {showFAQ && (
              <View style={styles.faqContent}>
                <Text style={styles.faqTitle}>Frequently Asked Questions</Text>
                {faqData.map((item, index) => (
                  <View key={index} style={styles.faqItem}>
                    <Text style={styles.faqQuestion}>Q: {item.question}</Text>
                    <Text style={styles.faqAnswer}>A: {item.answer}</Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#e3f2fd', // Light blue background
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  headerContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#0d47a1', // Deep blue
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#1976d2', // Medium blue
    textAlign: 'center',
  },
  formContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#81c784', // Light green border
  },
  inputContainer: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0d47a1', // Deep blue
    marginBottom: 8,
  },
  input: {
    borderWidth: 2,
    borderColor: '#42a5f5', // Medium blue
    borderRadius: 8,
    padding: 14,
    fontSize: 16,
    backgroundColor: '#f3e5f5', // Very light purple-blue
  },
  forgotPasswordContainer: {
    alignItems: 'flex-end',
    marginBottom: 24,
  },
  forgotPasswordText: {
    color: '#388e3c', // Medium green
    fontSize: 14,
    fontWeight: '500',
  },
  loginButton: {
    backgroundColor: '#1976d2', // Blue background
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#4caf50', // Green border
  },
  loginButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
  },
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  toggleText: {
    fontSize: 14,
    color: '#1976d2', // Medium blue
  },
  toggleLink: {
    fontSize: 14,
    color: '#388e3c', // Medium green
    fontWeight: '600',
  },
  faqContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    borderWidth: 1,
    borderColor: '#42a5f5', // Medium blue border
  },
  faqToggle: {
    alignItems: 'center',
    padding: 10,
    backgroundColor: '#e8f5e8', // Very light green
    borderRadius: 8,
  },
  faqToggleText: {
    color: '#2e7d32', // Dark green
    fontSize: 16,
    fontWeight: '600',
  },
  faqContent: {
    marginTop: 16,
  },
  faqTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#0d47a1', // Deep blue
    marginBottom: 16,
  },
  faqItem: {
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#81c784', // Light green
  },
  faqQuestion: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1976d2', // Medium blue
    marginBottom: 4,
  },
  faqAnswer: {
    fontSize: 14,
    color: '#388e3c', // Medium green
    lineHeight: 20,
  },
});

export default LoginPage;