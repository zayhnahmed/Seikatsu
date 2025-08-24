import Calendar from "@/components/home/Calendar";
import Overview from "@/components/home/Overview";
import Stats from "@/components/home/Stats";
import Tasks from "@/components/home/Tasks";
import { useRef, useState } from "react";
import { Animated, NativeScrollEvent, NativeSyntheticEvent, ScrollView, Text, TouchableOpacity, View } from "react-native";

export default function HomeTabs({ globalHeaderHeight = 80 }) {
  const [activeTab, setActiveTab] = useState("Overview");
  const scrollY = useRef(new Animated.Value(0)).current;
  const headerTranslateY = useRef(new Animated.Value(0)).current;
  const lastScrollY = useRef(0);
  const tabHeaderHeight = 80;

  const handleScroll = Animated.event(
    [{ nativeEvent: { contentOffset: { y: scrollY } } }],
    {
      useNativeDriver: false,
      listener: (event: NativeSyntheticEvent<NativeScrollEvent>) => {
        const currentScrollY = event.nativeEvent.contentOffset.y;
        const diff = currentScrollY - lastScrollY.current;

        if (diff > 0 && currentScrollY > 50) {
          Animated.timing(headerTranslateY, {
            toValue: -tabHeaderHeight,
            duration: 200,
            useNativeDriver: true,
          }).start();
        } else if (diff < 0) {
          Animated.timing(headerTranslateY, {
            toValue: 0,
            duration: 200,
            useNativeDriver: true,
          }).start();
        }

        lastScrollY.current = currentScrollY;
      },
    }
  );

  const tabs = ["Overview", "Tasks", "Calendar", "Stats"];

  const renderTabContent = () => {
    switch (activeTab) {
      case "Overview":
        return <Overview />;
      case "Tasks":
        return <Tasks />;
      case "Calendar":
        return <Calendar />;
      case "Stats":
        return <Stats />;
      default:
        return null;
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: "#371931" }}>
      {/*Tab Header */}
      <Animated.View
        style={{
          transform: [{ translateY: headerTranslateY }],
          position: "absolute",
          top: globalHeaderHeight,
          left: 0,
          right: 0,
          zIndex: 50,
          backgroundColor: "#371931",
          paddingVertical: 16,
        }}
      >
        <View
          style={{
            backgroundColor: "#2C1127",
            borderRadius: 16,
            padding: 2,
            marginHorizontal: 16,
          }}
        >
          <View style={{ flexDirection: "row", alignItems: "center" }}>
            {tabs.map((tab) => (
              <TouchableOpacity
                key={tab}
                onPress={() => setActiveTab(tab)}
                style={{
                  flex: 1,
                  backgroundColor: activeTab === tab ? "#FECD8A" : "transparent",
                  paddingHorizontal: 8,
                  paddingVertical: 12,
                  borderRadius: 12,
                  marginHorizontal: 1,
                }}
              >
                <Text
                  numberOfLines={1}
                  style={{
                    color: activeTab === tab ? "#371931" : "#B37BA4",
                    fontSize: 12,
                    fontWeight: activeTab === tab ? "600" : "500",
                    textAlign: "center",
                  }}
                >
                  {tab}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </Animated.View>

      {/* Scrollable Content */}
      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={{
          paddingTop: globalHeaderHeight + tabHeaderHeight + 20,
          paddingHorizontal: 24,
          paddingBottom: 100,
        }}
        onScroll={handleScroll}
        scrollEventThrottle={16}
        showsVerticalScrollIndicator={false}
      >
        {renderTabContent()}
      </ScrollView>
    </View>
  );
}
