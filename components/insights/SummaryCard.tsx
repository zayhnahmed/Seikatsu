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
    <View className="items-center justify-center relative">
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
      <View className="absolute inset-0 items-center justify-center">
        <Text className="text-xs font-bold text-gray-800">
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
  const getCardClasses = () => {
    const baseClasses = "rounded-2xl p-4 m-2 flex-1 border shadow-sm";
    
    switch (variant) {
      case 'primary':
        return `${baseClasses} bg-blue-500 border-blue-700`;
      case 'accent':
        return `${baseClasses} bg-yellow-100 border-yellow-200`;
      case 'success':
        return `${baseClasses} bg-green-100 border-green-200`;
      case 'secondary':
        return `${baseClasses} bg-gray-200 border-gray-300`;
      default:
        return `${baseClasses} bg-gray-50 border-gray-200`;
    }
  };

  const getTitleClasses = () => {
    const baseClasses = "text-sm font-medium flex-1";
    
    switch (variant) {
      case 'primary':
        return `${baseClasses} text-white`;
      default:
        return `${baseClasses} text-gray-800`;
    }
  };

  const getValueClasses = () => {
    const baseClasses = "text-xl font-bold mb-1";
    
    switch (variant) {
      case 'primary':
        return `${baseClasses} text-white`;
      default:
        return `${baseClasses} text-gray-800`;
    }
  };

  const getSubtitleClasses = () => {
    const baseClasses = "text-xs";
    
    switch (variant) {
      case 'primary':
        return `${baseClasses} text-white/80`;
      default:
        return `${baseClasses} text-gray-600`;
    }
  };

  const CardContent = () => (
    <View className={getCardClasses()} style={{ minWidth: 160 }}>
      <View className="flex-row items-center justify-between mb-3">
        <View className="flex-row items-center flex-1">
          <Text className="text-xl mr-2">{emoji}</Text>
          <Text className={getTitleClasses()}>
            {title}
          </Text>
        </View>
        {progress !== undefined && (
          <CircularProgress progress={progress} size={50} strokeWidth={4} />
        )}
      </View>
      <Text className={getValueClasses()}>
        {value}
      </Text>
      {subtitle && (
        <Text className={getSubtitleClasses()}>
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