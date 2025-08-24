import { Skill } from "@/types";
import { Apple, BookOpen, Briefcase, Dumbbell, Heart, Moon, Sparkles } from "lucide-react-native";
import React, { useEffect, useState } from 'react';
import { Animated, Dimensions, StatusBar, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { Gesture, GestureHandlerRootView } from 'react-native-gesture-handler';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface SkillConstellationProps {
  skill: Skill;
}

const SkillConstellation: React.FC<SkillConstellationProps> = ({ skill }) => {
  const [glowAnim] = useState(new Animated.Value(0));
  
  useEffect(() => {
    if (skill.leveledUpToday) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(glowAnim, {
            toValue: 1,
            duration: 1500,
            useNativeDriver: true,
          }),
          Animated.timing(glowAnim, {
            toValue: 0,
            duration: 1500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    }
  }, [skill.leveledUpToday, glowAnim]);

  const glowOpacity = glowAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0.3, 1],
  });

  const progressPercent = (skill.xp / skill.maxXp) * 100;
  const isMaxed = skill.xp >= skill.maxXp;

  return (
    <View style={styles.constellationContainer}>
      {/* Cosmic Background */}
      <View style={styles.cosmicBackground}>
        {/* Stars scattered around */}
        {Array.from({ length: 20 }, (_, i) => (
          <View
            key={i}
            style={[
              styles.star,
              {
                left: `${Math.random() * 90 + 5}%`,
                top: `${Math.random() * 80 + 10}%`,
                opacity: Math.random() * 0.8 + 0.2,
              },
            ]}
          />
        ))}
        
        {/* Constellation lines */}
        <View style={styles.constellationLines} />
      </View>

      {/* Skill Header */}
      <View style={styles.skillHeader}>
        <Text style={styles.skillName}>{skill.name.toUpperCase()}</Text>
        <Text style={styles.skillLevel}>LEVEL {skill.level}</Text>
        <Text style={styles.skillDescription}>{skill.description}</Text>
      </View>

      {/* Central Skill Node */}
      <View style={styles.centralNode}>
        {/* Glow effect for level ups */}
        {skill.leveledUpToday && (
          <Animated.View 
            style={[styles.nodeGlow, { opacity: glowOpacity }]}
          />
        )}
        
        {/* Main skill orb with solid colors (fallback) */}
        <TouchableOpacity 
          style={[
            styles.skillOrb,
            { backgroundColor: isMaxed ? '#FFD700' : '#87CEEB' }
          ]}
        >
          <skill.icon 
            size={40} 
            color={isMaxed ? '#1a1a1a' : '#FFFFFF'} 
          />
        </TouchableOpacity>
        
        {/* Skill progress ring */}
        <View style={styles.progressRing}>
          <View 
            style={[
              styles.progressArc,
              {
                transform: [{ rotate: `${(progressPercent / 100) * 360}deg` }]
              }
            ]}
          />
        </View>
      </View>

      {/* XP Info */}
      <View style={styles.xpInfo}>
        <Text style={styles.xpText}>
          {skill.xp} / {skill.maxXp} XP
        </Text>
        {skill.xpGainedToday > 0 && (
          <Text style={styles.xpGained}>+{skill.xpGainedToday} XP Today</Text>
        )}
      </View>

      {/* Level Up Notification */}
      {isMaxed && (
        <View style={styles.levelUpNotification}>
          <Text style={styles.levelUpText}>⭐ SKILL POINT AVAILABLE ⭐</Text>
        </View>
      )}

      {/* Perks indication */}
      <Text style={styles.perksText}>Perks to increase: 3</Text>
    </View>
  );
};

export default function Overview() {
  const [currentSkillIndex, setCurrentSkillIndex] = useState(0);
  const [translateX] = useState(new Animated.Value(0));

  const skills: Skill[] = [
    { 
      name: "Strength", 
      icon: Dumbbell, 
      xp: 40, 
      level: 4, 
      maxXp: 100, 
      xpGainedToday: 15,
      leveledUpToday: false,
      description: "The more powerful the warrior, the stronger the weapons and armor they can wield."
    },
    { 
      name: "Learning", 
      icon: BookOpen, 
      xp: 20, 
      level: 2, 
      maxXp: 100, 
      xpGainedToday: 25,
      leveledUpToday: false,
      description: "Knowledge and wisdom unlock the secrets of intellectual mastery."
    },
    { 
      name: "Sleep", 
      icon: Moon, 
      xp: 95, 
      level: 5, 
      maxXp: 100, 
      xpGainedToday: 5,
      leveledUpToday: false,
      description: "Rest and recovery are the foundation of all other skills."
    },
    { 
      name: "Nutrition", 
      icon: Apple, 
      xp: 55, 
      level: 3, 
      maxXp: 100, 
      xpGainedToday: 10,
      leveledUpToday: false,
      description: "Dietary wisdom fuels the body and mind for greater achievements."
    },
    { 
      name: "Career", 
      icon: Briefcase, 
      xp: 100, 
      level: 1, 
      maxXp: 100, 
      xpGainedToday: 30,
      leveledUpToday: true,
      description: "Professional mastery opens doors to wealth and influence."
    },
    { 
      name: "Relationship", 
      icon: Heart, 
      xp: 70, 
      level: 4, 
      maxXp: 100, 
      xpGainedToday: 8,
      leveledUpToday: false,
      description: "Social bonds and empathy create powerful connections with others."
    },
    { 
      name: "Spirituality", 
      icon: Sparkles, 
      xp: 5, 
      level: 1, 
      maxXp: 100, 
      xpGainedToday: 0,
      leveledUpToday: false,
      description: "Inner peace and mindfulness unlock the deepest mysteries of existence."
    },
  ];

  const panGesture = Gesture.Pan()
    .onUpdate((event) => {
      translateX.setValue(event.translationX);
    })
    .onEnd((event) => {
      const { translationX } = event;
      
      let nextIndex = currentSkillIndex;
      
      if (translationX < -50) {
        nextIndex = Math.min(currentSkillIndex + 1, skills.length - 1);
      } else if (translationX > 50) {
        nextIndex = Math.max(currentSkillIndex - 1, 0);
      }
      
      setCurrentSkillIndex(nextIndex);
      
      Animated.spring(translateX, {
        toValue: 0,
        useNativeDriver: true,
      }).start();
    });

  return (
    <GestureHandlerRootView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000814" />
      
      {/* Header similar to Skyrim */}
      <View style={styles.header}>
        <View style={styles.headerBorder}>
          <Text style={styles.characterName}>Zayhn</Text>
          <Text style={styles.characterLevel}>LEVEL 12</Text>
        </View>
      </View>

      {/* Skill Navigation */}
      <View style={styles.skillNavigation}>
        {skills.map((skill, index) => (
          <TouchableOpacity
            key={index}
            onPress={() => setCurrentSkillIndex(index)}
            style={[
              styles.navDot,
              { 
                opacity: index === currentSkillIndex ? 1 : 0.5,
                backgroundColor: index === currentSkillIndex 
                  ? 'rgba(255, 215, 0, 0.8)' 
                  : 'rgba(255, 215, 0, 0.3)'
              }
            ]}
          >
            <skill.icon size={16} color="#FFD700" />
          </TouchableOpacity>
        ))}
      </View>

      {/* Main Skill Display */}
      <View style={styles.skillDisplayContainer}>
        <View style={styles.skillContainer}>
          <SkillConstellation skill={skills[currentSkillIndex]} />
        </View>
      </View>

    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#001d3d',
  },
  header: {
    paddingTop: StatusBar.currentHeight ? StatusBar.currentHeight + 20 : 50,
    paddingHorizontal: 20,
    alignItems: 'center',
    marginBottom: 20,
  },
  headerBorder: {
    borderColor: '#FFD700',
    borderWidth: 2,
    paddingHorizontal: 30,
    paddingVertical: 10,
    borderRadius: 5,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
  },
  characterName: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    letterSpacing: 2,
  },
  characterLevel: {
    color: '#FFD700',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 5,
  },
  characterRace: {
    color: '#CCCCCC',
    fontSize: 14,
    textAlign: 'center',
  },
  skillNavigation: {
    flexDirection: 'row',
    justifyContent: 'center',
    paddingVertical: 20,
    paddingHorizontal: 10,
    gap: 15,
  },
  navDot: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#FFD700',
  },
  skillDisplayContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  skillContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  constellationContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
    flex: 1,
  },
  cosmicBackground: {
    position: 'absolute',
    width: screenWidth,
    height: '100%',
    top: 0,
    left: 0,
  },
  star: {
    position: 'absolute',
    width: 2,
    height: 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 1,
  },
  constellationLines: {
    position: 'absolute',
    width: '100%',
    height: '100%',
  },
  skillHeader: {
    alignItems: 'center',
    marginBottom: 30,
  },
  skillName: {
    color: '#FFD700',
    fontSize: 32,
    fontWeight: 'bold',
    letterSpacing: 3,
    textAlign: 'center',
  },
  skillLevel: {
    color: '#FFFFFF',
    fontSize: 18,
    marginTop: 5,
    letterSpacing: 1,
  },
  skillDescription: {
    color: '#CCCCCC',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 10,
    paddingHorizontal: 20,
    fontStyle: 'italic',
    lineHeight: 20,
  },
  centralNode: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 30,
  },
  nodeGlow: {
    position: 'absolute',
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#FFD700',
    shadowColor: '#FFD700',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 20,
    elevation: 20,
  },
  skillOrb: {
    width: 100,
    height: 100,
    borderRadius: 50,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 3,
    borderColor: '#FFD700',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 10,
    zIndex: 2,
  },
  progressRing: {
    position: 'absolute',
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 3,
    borderColor: 'rgba(255, 215, 0, 0.3)',
    zIndex: 1,
  },
  progressArc: {
    position: 'absolute',
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 3,
    borderColor: '#FFD700',
    borderRightColor: 'transparent',
    borderBottomColor: 'transparent',
  },
  xpInfo: {
    alignItems: 'center',
    marginBottom: 15,
  },
  xpText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  xpGained: {
    color: '#32CD32',
    fontSize: 14,
    marginTop: 5,
  },
  levelUpNotification: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 5,
    marginBottom: 15,
    backgroundColor: '#FFD700',
  },
  levelUpText: {
    color: '#000000',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  perksText: {
    color: '#FFFFFF',
    fontSize: 14,
    textAlign: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    paddingHorizontal: 15,
    paddingVertical: 5,
    borderRadius: 3,
  },
});