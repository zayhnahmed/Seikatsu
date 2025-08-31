import AchievementsWidget from '@/components/insights/AchievementsWidget';
import CategoryBalance from '@/components/insights/CategoryBalance';
import HealthWidget from '@/components/insights/HealthWidget';
import MoodChart from '@/components/insights/MoodChart';
import SummaryCard from '@/components/insights/SummaryCard';
import WeeklyReflections from '@/components/insights/WeeklyReflections';
import React from 'react';
import { ScrollView, Text, View } from 'react-native';

// Sample data - you'll replace these with your actual data
const mockData = {
  // Summary data
  xp: 2840,
  level: 12,
  streak: 5,
  
  // Health data
  healthData: {
    steps: 8542,
    targetSteps: 10000,
    calories: 2340,
    sleepHours: 7.2,
    heartRate: 68,
    activeMinutes: 45
  },
  
  // Mood chart data
  moodData: {
    labels: ['Aug 25', 'Aug 26', 'Aug 27', 'Aug 28', 'Aug 29', 'Aug 30', 'Aug 31'],
    datasets: [
      {
        data: [7, 8, 6, 9, 7, 8, 9],
        color: (opacity = 1) => `rgba(168, 255, 203, ${opacity})`,
        strokeWidth: 2
      }
    ]
  },
  
  // Achievements data
  achievements: [
    { 
      id: 1,
      name: "Consistency Award", 
      description: "Logged 7 days straight", 
      date: "2024-08-25",
      category: "Habits",
      xpReward: 100,
      emoji: "🔥",
      rarity: "common" as const
    },
    { 
      id: 2,
      name: "Strength Master", 
      description: "Reached Level 5 in Strength", 
      date: "2024-08-20",
      category: "Fitness",
      xpReward: 250,
      emoji: "💪",
      rarity: "rare" as const
    }
  ],
  
  // Category balance data (placeholder - you'll need to define this based on your CategoryBalance component)
  categoryData: []
};

const Insights = () => {
  return (
    <View className="flex-1 bg-primary">
        <ScrollView 
                className="flex-1"
                contentContainerStyle={{ paddingTop: 160, paddingBottom: 80 }}
                showsVerticalScrollIndicator={false}
              >
        {/* Header */}
        <View className="px-6 pb-8">
            <Text className="text-2xl font-bold text-light-100">Insights</Text>
        </View>

        {/* 1. Summary Cards Row */}
        <View className="flex-row px-4 mb-4">
            <SummaryCard 
            title="XP"
            value={`${mockData.xp} XP`}
            subtitle={`Level ${mockData.level} → ${mockData.level + 1}`}
            emoji="⚡"
            progress={75}
            variant="success"
            onPress={() => console.log('XP card pressed')}
            />
            <SummaryCard 
            title="Streak"
            value={`${mockData.streak} days`}
            subtitle="Keep it up!"
            emoji="🔥"
            variant="accent"
            onPress={() => console.log('Streak card pressed')}
            />
        </View>
        
        {/* 2. Spider Radar (7 Categories) */}
        <CategoryBalance data={mockData.categoryData} />
        
        {/* 3. Mood & Emotion Trends */}
        <MoodChart 
            data={mockData.moodData}
            title="Weekly Mood Patterns"
            period="Last 7 days"
            onPeriodChange={() => console.log('Change period')}
        />
        
        {/* 4. Health Integration Widgets */}
        <HealthWidget 
            data={mockData.healthData}
            title="Health Dashboard"
            onMetricPress={(metric, value) => console.log(`${metric}: ${value}`)}
            onSyncPress={() => console.log('Syncing health data...')}
            lastSync="5 min ago"
        />
        
        {/* 5. AI Insights (Weekly Reflection card) */}
        <WeeklyReflections />
        
        {/* 6. Achievements */}
        <AchievementsWidget 
            achievements={mockData.achievements}
            title="Recent Achievements"
            maxDisplay={3}
            onAchievementPress={(achievement) => {
            console.log('Achievement pressed:', achievement.name);
            }}
            onViewAllPress={() => {
            console.log('View all achievements pressed');
            }}
        />
        
        {/* 7. Comparison - Placeholder for future implementation */}
        <View className="bg-light-100 rounded-2xl p-4 mx-4 mb-6">
            <Text className="text-lg font-semibold text-primary mb-2">Progress Comparison</Text>
            <Text className="text-sm text-primary/60 mb-4">Compare your progress with previous periods</Text>
            <View className="items-center py-8">
            <Text className="text-4xl mb-2">📊</Text>
            <Text className="text-primary/60 text-center">
                Coming soon!{'\n'}Advanced comparison analytics
            </Text>
            </View>
        </View>

        {/* Bottom padding */}
        <View className="pt-50" />
        </ScrollView>
    </View>
  );
};

export default Insights;