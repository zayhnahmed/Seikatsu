import { icons } from "@/constants/icons";
import { useEffect, useRef } from "react";
import { Animated, Image, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

  export default function GlobalHeader({ scrollY }: any) {
    const headerTranslateY = useRef(new Animated.Value(0)).current;
    const lastScrollY = useRef(0);
    const headerHeight = 80; // Approximate header height

    useEffect(() => {
      if (!scrollY) return;

      const listener = scrollY.addListener(({ value }: any) => {
        const currentScrollY = value;
        const diff = currentScrollY - lastScrollY.current;

        if (diff > 0 && currentScrollY > headerHeight) {
          // Scrolling down - hide header
          Animated.timing(headerTranslateY, {
            toValue: -headerHeight,
            duration: 200,
            useNativeDriver: true,
          }).start();
        } else if (diff < 0) {
          // Scrolling up - show header
          Animated.timing(headerTranslateY, {
            toValue: 0,
            duration: 200,
            useNativeDriver: true,
          }).start();
        }

        lastScrollY.current = currentScrollY;
      });

      return () => {
        scrollY.removeListener(listener);
      };
    }, [scrollY, headerTranslateY]);

    return (
      <Animated.View
        style={{
          transform: [{ translateY: headerTranslateY }],
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
        }}
      >
        <SafeAreaView style={{backgroundColor: '#371931'}} edges={['top']}>
          <View style={{ 
            flexDirection: 'row', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            paddingHorizontal: 24, 
            paddingVertical: 16 
          }}>
            <TouchableOpacity 
              activeOpacity={0.7} 
              style={{
                backgroundColor: '#2C1127',
                padding: 12,
                borderRadius: 50,
              }}
            >
              <Image source={icons.settings} style={{ width: 24, height: 24 }} tintColor="#fff" />
            </TouchableOpacity>

            <TouchableOpacity 
              activeOpacity={0.7} 
              style={{
                backgroundColor: '#2C1127',
                padding: 12,
                borderRadius: 50,
              }}
            >
              <Image source={icons.bell} style={{ width: 24, height: 24 }} tintColor="#fff" />
            </TouchableOpacity>
          </View>
        </SafeAreaView>
      </Animated.View>
    );
  }