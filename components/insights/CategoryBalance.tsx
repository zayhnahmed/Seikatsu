import React from 'react';
import { Text, TouchableOpacity, View } from 'react-native';

// Type definitions
interface CategoryItem {
  category: string;
  current: number;
  max: number;
  icon: string;
}

interface CategoryBalanceProps {
  data: CategoryItem[];
  title?: string;
  onCategoryPress?: (category: CategoryItem) => void;
  showPercentage?: boolean;
}

const CategoryBalance: React.FC<CategoryBalanceProps> = ({ 
  data, 
  title = "Category Balance",
  onCategoryPress,
  showPercentage = true 
}) => {
  const handleCategoryPress = (category: CategoryItem) => {
    if (onCategoryPress) {
      onCategoryPress(category);
    }
  };

  return (
    <View className="bg-light-100 rounded-2xl p-4 shadow-sm border border-light-200 mx-4 mb-4">
      <Text className="text-lg font-semibold text-primary mb-4">{title}</Text>
      
      {/* Category Progress Bars */}
      <View className="space-y-3">
        {data.map((item, index) => (
          <TouchableOpacity 
            key={index} 
            className="flex-row items-center active:opacity-70"
            onPress={() => handleCategoryPress(item)}
          >
            <Text className="text-lg mr-2">{item.icon}</Text>
            <Text className="text-sm font-medium text-primary w-20">{item.category}</Text>
            <View className="flex-1 ml-3">
              <View className="h-3 bg-light-200 rounded-full">
                <View 
                  className="h-3 bg-accent rounded-full transition-all duration-300"
                  style={{ width: `${item.current}%` }}
                />
              </View>
            </View>
            {showPercentage && (
              <Text className="text-sm font-bold text-accent ml-2 w-8">{item.current}%</Text>
            )}
          </TouchableOpacity>
        ))}
      </View>

      {/* Summary Stats */}
      <View className="mt-4 pt-4 border-t border-light-200">
        <View className="flex-row justify-between">
          <View className="items-center">
            <Text className="text-xs text-primary/60 mb-1">Average</Text>
            <Text className="text-sm font-bold text-primary">
              {Math.round(data.reduce((sum, item) => sum + item.current, 0) / data.length)}%
            </Text>
          </View>
          <View className="items-center">
            <Text className="text-xs text-primary/60 mb-1">Highest</Text>
            <Text className="text-sm font-bold text-success">
              {Math.max(...data.map(item => item.current))}%
            </Text>
          </View>
          <View className="items-center">
            <Text className="text-xs text-primary/60 mb-1">Lowest</Text>
            <Text className="text-sm font-bold text-alert">
              {Math.min(...data.map(item => item.current))}%
            </Text>
          </View>
        </View>
      </View>
    </View>
  );
};

export default CategoryBalance;

// Usage Example:
/*
const categoryData: CategoryItem[] = [
  { category: 'Strength', current: 72, max: 100, icon: '🏋️' },
  { category: 'Learning', current: 85, max: 100, icon: '📚' },
  { category: 'Relationships', current: 68, max: 100, icon: '❤️' },
  { category: 'Spirituality', current: 75, max: 100, icon: '🌿' },
  { category: 'Career', current: 82, max: 100, icon: '💼' },
  { category: 'Sleep', current: 65, max: 100, icon: '😴' },
  { category: 'Nutrition', current: 78, max: 100, icon: '🍎' }
];

<CategoryBalance 
  data={categoryData}
  title="Life Balance Overview"
  onCategoryPress={(category) => console.log('Category pressed:', category)}
  showPercentage={true}
/>
*/