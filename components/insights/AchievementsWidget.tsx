import React, { useState } from 'react';
import { Text, TouchableOpacity, View } from 'react-native';

// Type definitions
type AchievementVariant = 'default' | 'recent' | 'rare';
type AchievementRarity = 'common' | 'rare' | 'legendary';

interface Achievement {
  id: number;
  name: string;
  description: string;
  date: string;
  category?: string;
  xpReward?: number;
  emoji?: string;
  rarity?: AchievementRarity;
}

interface AchievementCardProps {
  achievement: Achievement;
  onPress?: (achievement: Achievement) => void;
  variant?: AchievementVariant;
}

interface AchievementsWidgetProps {
  achievements?: Achievement[];
  title?: string;
  showAll?: boolean;
  onAchievementPress?: (achievement: Achievement) => void;
  onViewAllPress?: () => void;
  maxDisplay?: number;
}

const AchievementCard: React.FC<AchievementCardProps> = ({ 
  achievement, 
  onPress, 
  variant = 'default' 
}) => {
  const variantStyles: Record<AchievementVariant, string> = {
    default: 'bg-secondary/20 border-secondary/30',
    recent: 'bg-success/10 border-success/30',
    rare: 'bg-accent/20 border-accent/30'
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <TouchableOpacity 
      className={`flex-row items-center p-3 ${variantStyles[variant]} rounded-xl mb-2 active:opacity-70`}
      onPress={() => onPress && onPress(achievement)}
    >
      <View className="mr-3">
        <Text className="text-2xl">{achievement.emoji || '🏆'}</Text>
      </View>
      <View className="flex-1">
        <Text className="font-medium text-primary">{achievement.name}</Text>
        <Text className="text-sm text-primary/70 mt-1">{achievement.description}</Text>
        {achievement.category && (
          <Text className="text-xs text-accent mt-1 font-medium">
            {achievement.category}
          </Text>
        )}
      </View>
      <View className="items-end">
        <Text className="text-xs text-primary/50 mb-1">
          {formatDate(achievement.date)}
        </Text>
        {achievement.xpReward && (
          <Text className="text-xs text-success font-bold">
            +{achievement.xpReward} XP
          </Text>
        )}
      </View>
    </TouchableOpacity>
  );
};

const AchievementsWidget: React.FC<AchievementsWidgetProps> = ({ 
  achievements = [],
  title = "Recent Achievements",
  showAll = false,
  onAchievementPress,
  onViewAllPress,
  maxDisplay = 3 
}) => {
  const [expanded, setExpanded] = useState<boolean>(false);
  
  const displayAchievements = showAll || expanded 
    ? achievements 
    : achievements.slice(0, maxDisplay);

  const handleAchievementPress = (achievement: Achievement) => {
    if (onAchievementPress) {
      onAchievementPress(achievement);
    }
  };

  const handleViewAllPress = () => {
    if (onViewAllPress) {
      onViewAllPress();
    } else {
      setExpanded(!expanded);
    }
  };

  // Determine achievement variant based on recency and rarity
  const getAchievementVariant = (achievement: Achievement): AchievementVariant => {
    const date = new Date(achievement.date);
    const now = new Date();
    const diffDays = Math.abs(now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24);
    
    if (achievement.rarity === 'rare') return 'rare';
    if (diffDays <= 3) return 'recent';
    return 'default';
  };

  const totalXP = achievements.reduce((sum, achievement) => 
    sum + (achievement.xpReward || 0), 0
  );

  return (
    <View className="bg-light-100 rounded-2xl p-4 shadow-sm border border-light-200 mx-4 mb-4">
      {/* Header */}
      <View className="flex-row items-center justify-between mb-4">
        <View className="flex-1">
          <Text className="text-lg font-semibold text-primary">{title}</Text>
          <Text className="text-xs text-primary/60 mt-1">
            {achievements.length} total • +{totalXP} XP earned
          </Text>
        </View>
        {achievements.length > maxDisplay && !showAll && (
          <TouchableOpacity 
            className="bg-accent/10 px-3 py-2 rounded-lg"
            onPress={handleViewAllPress}
          >
            <Text className="text-xs text-accent font-medium">
              {expanded ? 'Show Less' : 'View All'}
            </Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Achievements List */}
      <View>
        {displayAchievements.length > 0 ? (
          displayAchievements.map((achievement, index) => (
            <AchievementCard
              key={achievement.id || index}
              achievement={achievement}
              variant={getAchievementVariant(achievement)}
              onPress={handleAchievementPress}
            />
          ))
        ) : (
          <View className="items-center py-8">
            <Text className="text-4xl mb-2">🎯</Text>
            <Text className="text-primary/60 text-center">
              No achievements yet.{'\n'}Complete activities to earn rewards!
            </Text>
          </View>
        )}
      </View>

      {/* Quick Stats */}
      {achievements.length > 0 && (
        <View className="mt-4 pt-4 border-t border-light-200">
          <View className="flex-row justify-between">
            <View className="items-center">
              <Text className="text-xs text-primary/60 mb-1">This Week</Text>
              <Text className="text-sm font-bold text-success">
                {achievements.filter(a => {
                  const date = new Date(a.date);
                  const weekAgo = new Date();
                  weekAgo.setDate(weekAgo.getDate() - 7);
                  return date >= weekAgo;
                }).length}
              </Text>
            </View>
            <View className="items-center">
              <Text className="text-xs text-primary/60 mb-1">Streak</Text>
              <Text className="text-sm font-bold text-accent">5 days</Text>
            </View>
            <View className="items-center">
              <Text className="text-xs text-primary/60 mb-1">Next Goal</Text>
              <Text className="text-sm font-bold text-primary">Level 13</Text>
            </View>
          </View>
        </View>
      )}
    </View>
  );
};

export default AchievementsWidget;

// Usage Example:
/*
const achievementsData: Achievement[] = [
  { 
    id: 1,
    name: "🔥 Consistency Award", 
    description: "Logged 7 days straight", 
    date: "2024-08-25",
    category: "Habits",
    xpReward: 100,
    emoji: "🔥",
    rarity: "common"
  },
  { 
    id: 2,
    name: "💪 Strength Master", 
    description: "Reached Level 5 in Strength", 
    date: "2024-08-20",
    category: "Fitness",
    xpReward: 250,
    emoji: "💪",
    rarity: "rare"
  },
  { 
    id: 3,
    name: "📚 Knowledge Seeker", 
    description: "100 hours of learning logged", 
    date: "2024-08-15",
    category: "Learning",
    xpReward: 500,
    emoji: "📚",
    rarity: "rare"
  }
];

<AchievementsWidget 
  achievements={achievementsData}
  title="Your Achievements"
  maxDisplay={3}
  onAchievementPress={(achievement) => console.log('Achievement:', achievement)}
  onViewAllPress={() => console.log('View all achievements')}
/>
*/