import React, { useState } from 'react';
import { Text, TouchableOpacity, View } from 'react-native';

// Type definitions
type InsightVariant = 'default' | 'positive' | 'negative' | 'neutral' | 'action';
type ReflectionType = 'daily' | 'weekly' | 'monthly' | 'custom';

interface InsightTagData {
  label: string;
  variant?: InsightVariant;
}

interface InsightTagProps {
  label: string;
  variant?: InsightVariant;
  onPress?: (label: string) => void;
}

interface WeeklyReflectionProps {
  insight?: string;
  title?: string;
  type?: ReflectionType;
  confidence?: number | null;
  tags?: (InsightTagData | string)[];
  suggestions?: string[];
  onSuggestionPress?: (suggestion: string) => void;
  onRegeneratePress?: () => void;
  onFeedbackPress?: (helpful: boolean) => void;
  isLoading?: boolean;
}

const InsightTag: React.FC<InsightTagProps> = ({ label, variant = 'default', onPress }) => {
  const variantStyles: Record<InsightVariant, string> = {
    default: 'bg-light-200 text-primary',
    positive: 'bg-success/20 text-success',
    negative: 'bg-alert/20 text-alert', 
    neutral: 'bg-accent/20 text-accent',
    action: 'bg-secondary/30 text-primary'
  };

  return (
    <TouchableOpacity 
      className={`px-3 py-1 rounded-full mr-2 mb-2 ${variantStyles[variant]}`}
      onPress={() => onPress && onPress(label)}
    >
      <Text className={`text-xs font-medium ${variantStyles[variant].split(' ')[1]}`}>
        {label}
      </Text>
    </TouchableOpacity>
  );
};

const WeeklyReflection: React.FC<WeeklyReflectionProps> = ({ 
  insight,
  title = "AI Weekly Reflection",
  type = "weekly",
  confidence = null,
  tags = [],
  suggestions = [],
  onSuggestionPress,
  onRegeneratePress,
  onFeedbackPress,
  isLoading = false 
}) => {
  const [expanded, setExpanded] = useState<boolean>(false);
  
  const typeEmojis: Record<ReflectionType, string> = {
    daily: '☀️',
    weekly: '🧠', 
    monthly: '📊',
    custom: '🔍'
  };

  const typeLabels: Record<ReflectionType, string> = {
    daily: 'Daily Insight',
    weekly: 'Weekly Reflection',
    monthly: 'Monthly Review',
    custom: 'Personal Analysis'
  };

  const handleSuggestionPress = (suggestion: string) => {
    if (onSuggestionPress) {
      onSuggestionPress(suggestion);
    }
  };

  const handleRegeneratePress = () => {
    if (onRegeneratePress) {
      onRegeneratePress();
    }
  };

  const handleFeedbackPress = (helpful: boolean) => {
    if (onFeedbackPress) {
      onFeedbackPress(helpful);
    }
  };

  const truncatedInsight = insight && insight.length > 200 && !expanded 
    ? insight.substring(0, 200) + '...' 
    : insight;

  // Helper function to get tag properties
  const getTagProps = (tag: InsightTagData | string): InsightTagData => {
    if (typeof tag === 'string') {
      return { label: tag, variant: 'default' };
    }
    return tag;
  };

  return (
    <View className="bg-gradient-to-r from-accent/10 to-secondary/20 rounded-2xl p-4 mx-4 mb-4 border border-accent/30">
      {/* Header */}
      <View className="flex-row items-center justify-between mb-3">
        <View className="flex-row items-center flex-1">
          <Text className="text-2xl mr-2">{typeEmojis[type]}</Text>
          <View className="flex-1">
            <Text className="text-lg font-semibold text-primary">
              {title || typeLabels[type]}
            </Text>
            {confidence && (
              <View className="flex-row items-center mt-1">
                <Text className="text-xs text-primary/60 mr-2">Confidence:</Text>
                <View className="flex-1 h-1 bg-light-200 rounded-full mr-2">
                  <View 
                    className="h-1 bg-accent rounded-full"
                    style={{ width: `${confidence}%` }}
                  />
                </View>
                <Text className="text-xs text-accent font-medium">{confidence}%</Text>
              </View>
            )}
          </View>
        </View>
        <TouchableOpacity 
          className="bg-light-200/50 p-2 rounded-lg"
          onPress={handleRegeneratePress}
        >
          <Text className="text-primary">🔄</Text>
        </TouchableOpacity>
      </View>

      {/* Insight Content */}
      <View className="mb-4">
        {isLoading ? (
          <View className="items-center py-4">
            <Text className="text-2xl mb-2">🤔</Text>
            <Text className="text-primary/60">Analyzing your data...</Text>
          </View>
        ) : (
          <>
            <Text className="text-primary/80 leading-6 mb-3">
              {truncatedInsight}
            </Text>
            {insight && insight.length > 200 && (
              <TouchableOpacity onPress={() => setExpanded(!expanded)}>
                <Text className="text-accent font-medium text-sm">
                  {expanded ? 'Show Less' : 'Read More'}
                </Text>
              </TouchableOpacity>
            )}
          </>
        )}
      </View>

      {/* Tags */}
      {tags.length > 0 && (
        <View className="mb-4">
          <Text className="text-xs text-primary/60 mb-2">Key Insights:</Text>
          <View className="flex-row flex-wrap">
            {tags.map((tag, index) => {
              const tagProps = getTagProps(tag);
              return (
                <InsightTag 
                  key={index} 
                  label={tagProps.label} 
                  variant={tagProps.variant || 'default'}
                />
              );
            })}
          </View>
        </View>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <View className="mb-4">
          <Text className="text-xs text-primary/60 mb-2">Recommendations:</Text>
          {suggestions.slice(0, expanded ? suggestions.length : 2).map((suggestion, index) => (
            <TouchableOpacity
              key={index}
              className="flex-row items-center p-2 bg-secondary/20 rounded-lg mb-2"
              onPress={() => handleSuggestionPress(suggestion)}
            >
              <Text className="text-sm mr-2">💡</Text>
              <Text className="text-sm text-primary flex-1">{suggestion}</Text>
              <Text className="text-accent text-xs">→</Text>
            </TouchableOpacity>
          ))}
          {suggestions.length > 2 && !expanded && (
            <TouchableOpacity onPress={() => setExpanded(true)}>
              <Text className="text-accent font-medium text-sm text-center">
                +{suggestions.length - 2} more suggestions
              </Text>
            </TouchableOpacity>
          )}
        </View>
      )}

      {/* Footer Actions */}
      <View className="flex-row items-center justify-between pt-3 border-t border-light-200/50">
        <View className="flex-row items-center">
          <Text className="text-xs text-primary/60 mr-3">Was this helpful?</Text>
          <TouchableOpacity 
            className="mr-2 p-1"
            onPress={() => handleFeedbackPress(true)}
          >
            <Text className="text-success">👍</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            className="p-1"
            onPress={() => handleFeedbackPress(false)}
          >
            <Text className="text-alert">👎</Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity className="flex-row items-center">
          <Text className="text-xs text-accent font-medium mr-1">Share</Text>
          <Text className="text-accent">📤</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default WeeklyReflection;

// Usage Example:
/*
const insightData = {
  insight: "This week shows excellent progress in Strength (+27%) and Learning (+16%). However, your Sleep category has declined significantly (-25%), which may be impacting your Relationships score. Consider prioritizing earlier bedtimes to boost overall well-being. Focus suggestion for next week: Establish a wind-down routine to improve sleep quality.",
  confidence: 85,
  tags: [
    { label: "Sleep Decline", variant: "negative" as InsightVariant },
    { label: "Strength Gain", variant: "positive" as InsightVariant },
    { label: "Learning Growth", variant: "positive" as InsightVariant }
  ] as InsightTagData[],
  suggestions: [
    "Set a consistent bedtime routine by 10 PM",
    "Try meditation before sleep",
    "Reduce screen time 1 hour before bed",
    "Consider sleep tracking for better insights"
  ]
};

<WeeklyReflection 
  insight={insightData.insight}
  title="Weekly Health Pattern"
  type="weekly"
  confidence={insightData.confidence}
  tags={insightData.tags}
  suggestions={insightData.suggestions}
  onSuggestionPress={(suggestion) => console.log('Suggestion:', suggestion)}
  onRegeneratePress={() => console.log('Regenerating insight...')}
  onFeedbackPress={(helpful) => console.log('Feedback:', helpful)}
  isLoading={false}
/>
*/