import React, { useState } from 'react';
import { Dimensions, Text, TouchableOpacity, View } from 'react-native';
import { LineChart } from 'react-native-chart-kit';

const screenWidth = Dimensions.get('window').width;

// Type definitions
interface ChartDataset {
  data: number[];
  color?: (opacity?: number) => string;
  strokeWidth?: number;
}

interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

interface MoodChartProps {
  data: ChartData;
  title?: string;
  period?: string;
  onPeriodChange?: () => void;
}

type MoodType = 'Happy' | 'Sad' | 'Angry' | 'Scared' | 'Confused';
type MoodSelection = MoodType | 'all';

const MoodChart: React.FC<MoodChartProps> = ({ 
  data, 
  title = "Mood Trends",
  period = "7 days",
  onPeriodChange 
}) => {
  const [selectedMood, setSelectedMood] = useState<MoodSelection>('all');

  const moodColors: Record<MoodType, string> = {
    Happy: '#A8FFCB',    // success
    Sad: '#FF8080',      // alert  
    Angry: '#FF8080',    // alert
    Scared: '#89CFF0',   // info
    Confused: '#B37BA4'  // accent
  };

  const moodEmojis: Record<MoodType, string> = {
    Happy: '😊',
    Sad: '😢',
    Angry: '😠',
    Scared: '😨',
    Confused: '🤔'
  };

  const chartConfig = {
    backgroundColor: '#F8E9D2',
    backgroundGradientFrom: '#F8E9D2',
    backgroundGradientTo: '#F3D8BE',
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(179, 123, 164, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(55, 25, 49, ${opacity})`,
    style: {
      borderRadius: 16
    },
    propsForDots: {
      r: '4',
      strokeWidth: '2',
      stroke: '#B37BA4'
    }
  };

  const handleMoodToggle = (mood: MoodType) => {
    setSelectedMood(selectedMood === mood ? 'all' : mood);
  };

  const handlePeriodPress = () => {
    if (onPeriodChange) {
      onPeriodChange();
    }
  };

  return (
    <View className="bg-light-100 rounded-2xl p-4 shadow-sm border border-light-200 mx-4 mb-4">
      {/* Header */}
      <View className="flex-row items-center justify-between mb-4">
        <Text className="text-lg font-semibold text-primary">{title}</Text>
        <TouchableOpacity 
          className="bg-secondary/20 px-3 py-1 rounded-lg"
          onPress={handlePeriodPress}
        >
          <Text className="text-xs text-primary font-medium">{period}</Text>
        </TouchableOpacity>
      </View>

      {/* Chart */}
      <View className="mb-4">
        <LineChart
          data={data}
          width={screenWidth - 64}
          height={220}
          yAxisInterval={1}
          chartConfig={chartConfig}
          bezier
          style={{
            borderRadius: 16
          }}
        />
      </View>

      {/* Mood Legend */}
      <View className="flex-row flex-wrap justify-center gap-3">
        {(Object.entries(moodEmojis) as [MoodType, string][]).map(([mood, emoji]) => (
          <TouchableOpacity
            key={mood}
            className={`flex-row items-center px-3 py-2 rounded-lg ${
              selectedMood === mood ? 'bg-accent/20' : 'bg-light-200'
            }`}
            onPress={() => handleMoodToggle(mood)}
          >
            <Text className="mr-1">{emoji}</Text>
            <View 
              className="w-3 h-3 rounded-full mr-2" 
              style={{ backgroundColor: moodColors[mood] }}
            />
            <Text className="text-xs text-primary font-medium">{mood}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Quick Stats */}
      <View className="mt-4 pt-4 border-t border-light-200">
        <View className="flex-row justify-between">
          <View className="items-center">
            <Text className="text-xs text-primary/60 mb-1">This Week</Text>
            <Text className="text-sm font-bold text-success">↗️ Improving</Text>
          </View>
          <View className="items-center">
            <Text className="text-xs text-primary/60 mb-1">Dominant</Text>
            <Text className="text-sm font-bold text-primary">😊 Happy</Text>
          </View>
          <View className="items-center">
            <Text className="text-xs text-primary/60 mb-1">Avg Score</Text>
            <Text className="text-sm font-bold text-accent">7.2/10</Text>
          </View>
        </View>
      </View>
    </View>
  );
};

export default MoodChart;

// Usage Example:
/*
const moodData: ChartData = {
  labels: ['Aug 25', 'Aug 26', 'Aug 27', 'Aug 28', 'Aug 29', 'Aug 30', 'Aug 31'],
  datasets: [
    {
      data: [7, 8, 6, 9, 7, 8, 9],
      color: (opacity = 1) => `rgba(168, 255, 203, ${opacity})`, // Happy
      strokeWidth: 2
    },
    {
      data: [2, 1, 3, 1, 2, 1, 0],
      color: (opacity = 1) => `rgba(255, 128, 128, ${opacity})`, // Sad
      strokeWidth: 2
    }
  ]
};

<MoodChart 
  data={moodData}
  title="Weekly Mood Patterns"
  period="Last 7 days"
  onPeriodChange={() => console.log('Change period')}
/>
*/