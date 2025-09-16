import React from 'react';
import { Text, TouchableOpacity, View } from 'react-native';
import Svg, { Circle } from 'react-native-svg';

// Type definitions
interface CircularProgressProps {
  progress: number;
  size?: number;
  strokeWidth?: number;
}

interface SummaryCardProps {
  title: string;
  value: string;
  subtitle?: string;
  emoji: string;
  progress?: number;
  variant?: 'default' | 'primary' | 'accent' | 'success' | 'secondary';
  onPress?: () => void;
}

// Circular Progress Component
const CircularProgress: React.FC<CircularProgressProps> = ({ progress, size = 50, strokeWidth = 4 }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (progress / 100) * circumference;
  
  return (
    <View style={{
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative'
    }}>
      <Svg 
        width={size} 
        height={size} 
        style={{ transform: [{ rotate: '-90deg' }] }}
      >
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#F3D8BE"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#B37BA4"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
        />
      </Svg>
      <View style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Text style={{
          fontSize: 12,
          fontWeight: 'bold',
          color: '#333'
        }}>
          {Math.round(progress)}%
        </Text>
      </View>
    </View>
  );
};

// Summary Card Component
const SummaryCard: React.FC<SummaryCardProps> = ({ 
  title, 
  value, 
  subtitle, 
  emoji, 
  progress, 
  variant = "default",
  onPress 
}) => {
  const cardStyles = {
    default: {
      backgroundColor: '#FAFAFA',
      borderColor: '#E5E5E5',
    },
    primary: {
      backgroundColor: '#007AFF',
      borderColor: '#0056CC',
    },
    accent: {
      backgroundColor: '#F79240',
      borderColor: '#EB6F0A',
    },
    success: {
      backgroundColor: '#4DD080',
      borderColor: '#009963',
    },
    secondary: {
      backgroundColor: 'rgba(108, 117, 125, 0.2)',
      borderColor: 'rgba(108, 117, 125, 0.3)',
    }
  };

  const textStyles = {
    default: { color: '#333' },
    primary: { color: '#FFFFFF' },
    accent: { color: '#333' },
    success: { color: '#333' },
    secondary: { color: '#333' }
  };

  const subtitleStyles = {
    default: { color: 'rgba(51, 51, 51, 0.6)' },
    primary: { color: 'rgba(255, 255, 255, 0.8)' },
    accent: { color: 'rgba(51, 51, 51, 0.7)' },
    success: { color: 'rgba(51, 51, 51, 0.7)' },
    secondary: { color: 'rgba(51, 51, 51, 0.7)' }
  };

  const cardStyle = {
    ...cardStyles[variant],
    borderRadius: 16,
    padding: 16,
    margin: 8,
    flex: 1,
    minWidth: 160,
    borderWidth: 1,
    // Shadow for iOS
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    // Elevation for Android
    elevation: 2,
  };

  const CardContent = () => (
    <View style={cardStyle}>
      <View style={{
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 12
      }}>
        <View style={{
          flexDirection: 'row',
          alignItems: 'center',
          flex: 1
        }}>
          <Text style={{ fontSize: 20, marginRight: 8 }}>{emoji}</Text>
          <Text style={{
            fontSize: 14,
            fontWeight: '500',
            flex: 1,
            ...textStyles[variant]
          }}>
            {title}
          </Text>
        </View>
        {progress !== undefined && (
          <CircularProgress progress={progress} size={50} strokeWidth={4} />
        )}
      </View>
      <Text style={{
        fontSize: 20,
        fontWeight: 'bold',
        marginBottom: 4,
        ...textStyles[variant]
      }}>
        {value}
      </Text>
      {subtitle && (
        <Text style={{
          fontSize: 12,
          ...subtitleStyles[variant]
        }}>
          {subtitle}
        </Text>
      )}
    </View>
  );

  if (onPress) {
    return (
      <TouchableOpacity onPress={onPress} activeOpacity={0.7}>
        <CardContent />
      </TouchableOpacity>
    );
  }

  return <CardContent />;
};

export default SummaryCard;

// Usage Example:
/*
<SummaryCard
  title="XP Progress"
  value="2840 XP"
  subtitle="Level 12 → 13"
  emoji="⚡"
  progress={75}
  variant="success"
  onPress={() => console.log('XP card pressed')}
/>
*/