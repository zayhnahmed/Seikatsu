import React from 'react';
import { Text, TouchableOpacity, View } from 'react-native';

// Type definitions
type VariantType = 'info' | 'alert' | 'accent' | 'secondary' | 'success';

interface HealthMetricCardProps {
  emoji: string;
  value: string;
  label: string;
  subtitle?: string;
  variant?: VariantType;
  progress?: number;
  onPress?: () => void;
}

interface HealthData {
  steps: number;
  targetSteps: number;
  calories: number;
  sleepHours: number;
  heartRate: number;
  activeMinutes?: number;
}

interface HealthWidgetProps {
  data: HealthData;
  title?: string;
  onMetricPress?: (metric: string, value: number) => void;
  onSyncPress?: () => void;
  lastSync?: string;
}

const HealthMetricCard: React.FC<HealthMetricCardProps> = ({ 
  emoji, 
  value, 
  label, 
  subtitle, 
  variant = 'info',
  progress,
  onPress 
}) => {
  const variantStyles: Record<VariantType, string> = {
    info: 'bg-info/20 border-info/30',
    alert: 'bg-alert/20 border-alert/30', 
    accent: 'bg-accent/20 border-accent/30',
    secondary: 'bg-secondary/30 border-secondary/40',
    success: 'bg-success/20 border-success/30'
  };

  const subtitleColors: Record<VariantType, string> = {
    info: 'text-info',
    alert: 'text-alert',
    accent: 'text-accent', 
    secondary: 'text-primary',
    success: 'text-success'
  };

  return (
    <TouchableOpacity 
      className={`${variantStyles[variant]} rounded-xl p-3 items-center border flex-1 mx-1 active:opacity-70`}
      onPress={onPress}
    >
      <Text className="text-2xl mb-1">{emoji}</Text>
      <Text className="text-lg font-bold text-primary">{value}</Text>
      <Text className="text-sm text-primary/70 text-center">{label}</Text>
      {subtitle && (
        <Text className={`text-xs mt-1 text-center ${subtitleColors[variant]}`}>
          {subtitle}
        </Text>
      )}
      {progress && (
        <View className="w-full mt-2">
          <View className="h-1 bg-light-200 rounded-full">
            <View 
              className={`h-1 rounded-full ${variant === 'info' ? 'bg-info' : 
                variant === 'alert' ? 'bg-alert' : 
                variant === 'accent' ? 'bg-accent' : 
                variant === 'secondary' ? 'bg-secondary' : 'bg-success'}`}
              style={{ width: `${progress}%` }}
            />
          </View>
        </View>
      )}
    </TouchableOpacity>
  );
};

const HealthWidget: React.FC<HealthWidgetProps> = ({ 
  data, 
  title = "Health Integration",
  onMetricPress,
  onSyncPress,
  lastSync 
}) => {
  const handleMetricPress = (metric: string, value: number) => {
    if (onMetricPress) {
      onMetricPress(metric, value);
    }
  };

  const handleSyncPress = () => {
    if (onSyncPress) {
      onSyncPress();
    }
  };

  const stepProgress = (data.steps / data.targetSteps) * 100;

  return (
    <View className="bg-light-100 rounded-2xl p-4 shadow-sm border border-light-200 mx-4 mb-4">
      {/* Header */}
      <View className="flex-row items-center justify-between mb-4">
        <Text className="text-lg font-semibold text-primary">{title}</Text>
        <TouchableOpacity 
          className="bg-accent/10 px-3 py-1 rounded-lg flex-row items-center"
          onPress={handleSyncPress}
        >
          <Text className="text-xs text-accent font-medium mr-1">Sync</Text>
          <Text className="text-xs">🔄</Text>
        </TouchableOpacity>
      </View>

      {/* Health Metrics Grid */}
      <View className="space-y-3">
        {/* Top Row */}
        <View className="flex-row">
          <HealthMetricCard
            emoji="👟"
            value={data.steps?.toLocaleString() || '0'}
            label="Steps"
            subtitle={`${Math.round(stepProgress)}% of goal`}
            variant="info"
            progress={stepProgress}
            onPress={() => handleMetricPress('steps', data.steps)}
          />
          <HealthMetricCard
            emoji="❤️"
            value={data.heartRate?.toString() || '0'}
            label="BPM"
            subtitle="Resting rate"
            variant="alert"
            onPress={() => handleMetricPress('heartRate', data.heartRate)}
          />
        </View>

        {/* Bottom Row */}
        <View className="flex-row">
          <HealthMetricCard
            emoji="🌙"
            value={`${data.sleepHours?.toString() || '0'}h`}
            label="Sleep"
            subtitle="Last night"
            variant="accent"
            onPress={() => handleMetricPress('sleep', data.sleepHours)}
          />
          <HealthMetricCard
            emoji="🔥"
            value={data.calories?.toString() || '0'}
            label="Calories"
            subtitle="Burned today"
            variant="secondary"
            onPress={() => handleMetricPress('calories', data.calories)}
          />
        </View>
      </View>

      {/* Summary Stats */}
      <View className="mt-4 pt-4 border-t border-light-200">
        <View className="flex-row justify-between">
          <View className="items-center">
            <Text className="text-xs text-primary/60 mb-1">Health Score</Text>
            <Text className="text-sm font-bold text-success">85/100</Text>
          </View>
          <View className="items-center">
            <Text className="text-xs text-primary/60 mb-1">Weekly Trend</Text>
            <Text className="text-sm font-bold text-accent">↗️ +12%</Text>
          </View>
          <View className="items-center">
            <Text className="text-xs text-primary/60 mb-1">Last Sync</Text>
            <Text className="text-sm font-bold text-primary">
              {lastSync || 'Just now'}
            </Text>
          </View>
        </View>
      </View>
    </View>
  );
};

export default HealthWidget;

// Usage Example:
/*
const healthData: HealthData = {
  steps: 8542,
  targetSteps: 10000,
  calories: 2340,
  sleepHours: 7.2,
  heartRate: 68,
  activeMinutes: 45
};

<HealthWidget 
  data={healthData}
  title="Health Dashboard"
  onMetricPress={(metric, value) => console.log(`${metric}: ${value}`)}
  onSyncPress={() => console.log('Syncing health data...')}
  lastSync="5 min ago"
/>
*/