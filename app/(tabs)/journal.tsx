import DateTimePicker from '@react-native-community/datetimepicker';
import React, { useState } from 'react';
import {
  Alert,
  ScrollView,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

interface JournalEntry {
  date: string;
  mood: string;
  strength: string;
  learning: string;
  relationships: string;
  spirituality: string;
  career: string;
  sleep: number;
  nutrition: string;
  reflection: string;
}

const Journal: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [selectedMood, setSelectedMood] = useState('');
  const [sleepHours, setSleepHours] = useState(8);
  
  // Form states for each category
  const [strength, setStrength] = useState('');
  const [learning, setLearning] = useState('');
  const [relationships, setRelationships] = useState('');
  const [spirituality, setSpirituality] = useState('');
  const [career, setCareer] = useState('');
  const [nutrition, setNutrition] = useState('');
  const [reflection, setReflection] = useState('');

  const moods = [
    { emoji: '🙂', label: 'Happy', value: 'happy' },
    { emoji: '😢', label: 'Sad', value: 'sad' },
    { emoji: '😡', label: 'Angry', value: 'angry' },
    { emoji: '😱', label: 'Scared', value: 'scared' },
    { emoji: '😕', label: 'Confused', value: 'confused' },
  ];

  const handleDateChange = (event: any, date?: Date) => {
    setShowDatePicker(false);
    if (date) {
      setSelectedDate(date);
    }
  };

  const handleSleepChange = (value: string) => {
    const hours = parseFloat(value) || 0;
    if (hours >= 0 && hours <= 24) {
      setSleepHours(hours);
    }
  };

  const incrementSleep = () => {
    if (sleepHours < 24) {
      setSleepHours(prev => Math.round((prev + 0.5) * 2) / 2); // Round to nearest 0.5
    }
  };

  const decrementSleep = () => {
    if (sleepHours > 0) {
      setSleepHours(prev => Math.round((prev - 0.5) * 2) / 2); // Round to nearest 0.5
    }
  };

  const handleSubmit = () => {
    // Validate required fields
    if (!selectedMood) {
      Alert.alert('Missing Information', 'Please select your mood for today.');
      return;
    }

    const entry: JournalEntry = {
      date: selectedDate.toISOString().split('T')[0],
      mood: selectedMood,
      strength,
      learning,
      relationships,
      spirituality,
      career,
      sleep: sleepHours,
      nutrition,
      reflection,
    };

    // TODO: Save to local storage or database
    console.log('Saving journal entry:', entry);
    Alert.alert('Success!', 'Your journal entry has been saved.');
    
    // Reset form (optional)
    resetForm();
  };

  const resetForm = () => {
    setSelectedMood('');
    setStrength('');
    setLearning('');
    setRelationships('');
    setSpirituality('');
    setCareer('');
    setSleepHours(8);
    setNutrition('');
    setReflection('');
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <View className="flex-1 bg-primary">
      <ScrollView 
        className="flex-1"
        contentContainerStyle={{ paddingTop: 160, paddingBottom: 80 }}
        showsVerticalScrollIndicator={false}
      >
        <View className="px-6 pb-8">
          {/* Header Section */}
          <View className="mb-6">
            <Text className="text-2xl font-bold text-light-100 mb-4">Daily Journal</Text>
            
            {/* Date Picker */}
            <TouchableOpacity
              onPress={() => setShowDatePicker(true)}
              className="bg-white rounded-xl p-4 mb-4 border border-light-300"
            >
              <Text className="text-primary font-semibold">
                📅 {formatDate(selectedDate)}
              </Text>
            </TouchableOpacity>

            {showDatePicker && (
              <DateTimePicker
                value={selectedDate}
                mode="date"
                display="default"
                onChange={handleDateChange}
              />
            )}

            {/* Mood Selector */}
            <View className="mb-6">
              <Text className="text-lg font-semibold text-primary mb-3">
                How are you feeling today?
              </Text>
              <View className="flex-row flex-wrap justify-between">
                {moods.map((mood) => (
                  <TouchableOpacity
                    key={mood.value}
                    onPress={() => setSelectedMood(mood.value)}
                    className={`p-3 rounded-xl border-2 mb-2 min-w-[60px] items-center ${
                      selectedMood === mood.value
                        ? 'border-accent bg-accent/20'
                        : 'border-light-300 bg-white'
                    }`}
                  >
                    <Text className="text-2xl mb-1">{mood.emoji}</Text>
                    <Text className={`text-xs font-medium ${
                      selectedMood === mood.value ? 'text-primary' : 'text-dark-100'
                    }`}>
                      {mood.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </View>

          {/* Daily Entry Form */}
          <View className="gap-6">
            {/* Strength */}
            <View className="bg-white rounded-xl p-4 border border-light-300">
              <Text className="text-lg font-semibold text-primary mb-2">
                💪 Strength
              </Text>
              <Text className="text-dark-100 mb-3">
                Did you work out today? What did you do?
              </Text>
              <TextInput
                value={strength}
                onChangeText={setStrength}
                placeholder="E.g., 30min run, yoga session, gym workout..."
                multiline
                numberOfLines={3}
                className="border border-light-300 rounded-lg p-3 text-dark-100"
                placeholderTextColor="#999"
              />
            </View>

            {/* Learning */}
            <View className="bg-white rounded-xl p-4 border border-light-300">
              <Text className="text-lg font-semibold text-primary mb-2">
                🧠 Learning
              </Text>
              <Text className="text-dark-100 mb-3">
                What did you learn today?
              </Text>
              <TextInput
                value={learning}
                onChangeText={setLearning}
                placeholder="New skills, insights, facts, or realizations..."
                multiline
                numberOfLines={3}
                className="border border-light-300 rounded-lg p-3 text-dark-100"
                placeholderTextColor="#999"
              />
            </View>

            {/* Relationships */}
            <View className="bg-white rounded-xl p-4 border border-light-300">
              <Text className="text-lg font-semibold text-primary mb-2">
                ❤️ Relationships
              </Text>
              <Text className="text-dark-100 mb-3">
                Did you connect with anyone meaningfully?
              </Text>
              <TextInput
                value={relationships}
                onChangeText={setRelationships}
                placeholder="Quality time with family, friends, colleagues..."
                multiline
                numberOfLines={3}
                className="border border-light-300 rounded-lg p-3 text-dark-100"
                placeholderTextColor="#999"
              />
            </View>

            {/* Spirituality */}
            <View className="bg-white rounded-xl p-4 border border-light-300">
              <Text className="text-lg font-semibold text-primary mb-2">
                🧘 Spirituality
              </Text>
              <Text className="text-dark-100 mb-3">
                Any meditation, reflection, or prayer today?
              </Text>
              <TextInput
                value={spirituality}
                onChangeText={setSpirituality}
                placeholder="Meditation, prayer, reflection, mindfulness..."
                multiline
                numberOfLines={3}
                className="border border-light-300 rounded-lg p-3 text-dark-100"
                placeholderTextColor="#999"
              />
            </View>

            {/* Career */}
            <View className="bg-white rounded-xl p-4 border border-light-300">
              <Text className="text-lg font-semibold text-primary mb-2">
                🚀 Career
              </Text>
              <Text className="text-dark-100 mb-3">
                Any progress at work/study?
              </Text>
              <TextInput
                value={career}
                onChangeText={setCareer}
                placeholder="Projects completed, skills developed, goals achieved..."
                multiline
                numberOfLines={3}
                className="border border-light-300 rounded-lg p-3 text-dark-100"
                placeholderTextColor="#999"
              />
            </View>

            {/* Sleep */}
            <View className="bg-white rounded-xl p-4 border border-light-300">
              <Text className="text-lg font-semibold text-primary mb-2">
                😴 Sleep
              </Text>
              <Text className="text-dark-100 mb-3">
                How many hours did you sleep?
              </Text>
              <View className="flex-row items-center">
                <TouchableOpacity
                  onPress={decrementSleep}
                  className="bg-light-200 rounded-lg p-2 mr-3"
                >
                  <Text className="text-primary font-bold text-xl">-</Text>
                </TouchableOpacity>
                
                <View className="flex-1 mx-3">
                  <TextInput
                    value={sleepHours.toString()}
                    onChangeText={handleSleepChange}
                    keyboardType="numeric"
                    className="border border-light-300 rounded-lg p-3 text-center text-xl font-semibold text-primary"
                  />
                </View>
                
                <TouchableOpacity
                  onPress={incrementSleep}
                  className="bg-light-200 rounded-lg p-2 ml-3"
                >
                  <Text className="text-primary font-bold text-xl">+</Text>
                </TouchableOpacity>
              </View>
              <Text className="text-center text-dark-100 mt-2">hours</Text>
            </View>

            {/* Nutrition */}
            <View className="bg-white rounded-xl p-4 border border-light-300">
              <Text className="text-lg font-semibold text-primary mb-2">
                🥗 Nutrition
              </Text>
              <Text className="text-dark-100 mb-3">
                What did you eat today?
              </Text>
              <TextInput
                value={nutrition}
                onChangeText={setNutrition}
                placeholder="Meals, snacks, water intake, notable food choices..."
                multiline
                numberOfLines={3}
                className="border border-light-300 rounded-lg p-3 text-dark-100"
                placeholderTextColor="#999"
              />
            </View>

            {/* Notes / Reflection */}
            <View className="bg-white rounded-xl p-4 border border-light-300">
              <Text className="text-lg font-semibold text-primary mb-2">
                📝 Reflection
              </Text>
              <Text className="text-dark-100 mb-3">
                Write anything you want to reflect on today — thoughts, mistakes, wins, etc.
              </Text>
              <TextInput
                value={reflection}
                onChangeText={setReflection}
                placeholder="Your thoughts, feelings, lessons learned, gratitudes..."
                multiline
                numberOfLines={5}
                className="border border-dark-100 rounded-lg p-3 text-dark-100"
                placeholderTextColor="#999"
              />
            </View>

            {/* Submit Button */}
            <TouchableOpacity
              onPress={handleSubmit}
              className="bg-light-100 rounded-xl p-4 mt-6 mb-8"
            >
              <Text className="text-dark-100 font-semibold text-lg text-center">
                Save
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </View>
  );
};

export default Journal;