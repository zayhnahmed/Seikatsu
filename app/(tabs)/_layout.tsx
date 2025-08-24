import HeaderBar from "@/components/HeaderBar";
import { icons } from "@/constants/icons";
import { images } from "@/constants/images";
import { Tabs } from "expo-router";
import { Image, ImageBackground, ImageSourcePropType, Text, View } from 'react-native';

type TabIconProps = {
  focused: boolean;
  icon: ImageSourcePropType;
  title: string;
};

const TabIcon = ({ focused, icon, title }: TabIconProps) => {
  if (focused) {
    return (
      <ImageBackground
        source={images.highlight}
        className="flex flex-row w-full flex-1 min-w-[112px] min-h-16 mt-4 justify-center items-center rounded-full overflow-hidden"
        style={{ backgroundColor: "#FECD8A" }} 
        imageStyle={{ opacity: 0.3 }} 
      >
        <Image source={icon} style={{ tintColor: "#2C1127" }} className="size-5" />
        <Text className="text-primary text-base font-semibold ml-2">{title}</Text>
      </ImageBackground>
    );
  }

  return (
    <View className="size-full justify-center items-center mt-4 rounded-full">
      <Image source={icon} style={{ tintColor: "#B37BA4" }} className="size-5" />
    </View>
  );
};

const _Layout = () => {
  return (
    <View className="flex-1 bg-[#1F0B19]">
      <HeaderBar />
      <Tabs
        screenOptions={{
          tabBarShowLabel: false,
          tabBarItemStyle: {
              width: '100%',
              height: '100%',
              justifyContent: 'center',
              alignItems: 'center'
          },
          tabBarStyle: {
            backgroundColor: "#1F0B19", 
            borderTopColor: "#2C1127",
            marginHorizontal: 10,
            marginBottom: 36,
            height: 52,
            borderRadius: 50,
            overflow: 'hidden',
            position: 'absolute',   
            borderColor: '#1F0B19',
          },
        }}
      >
        <Tabs.Screen
          name="index"
          options={{
            title: 'Home',
            headerShown: false,
            tabBarIcon: ({ focused }) => (
              <TabIcon focused={focused} icon={icons.home} title="Home" />
            ),
          }}
        />

        <Tabs.Screen
          name="journal"
          options={{
            title: 'Journal',
            headerShown: false,
            tabBarIcon: ({ focused }) => (
              <TabIcon focused={focused} icon={icons.journal} title="Journal" />
            ),
          }}
        />

        <Tabs.Screen
          name="insights"
          options={{
            title: 'Insights',
            headerShown: false,
            tabBarIcon: ({ focused }) => (
              <TabIcon focused={focused} icon={icons.insights} title="Insights" />
            ),
          }}
        />

        <Tabs.Screen
          name="market"
          options={{
            title: 'Market',
            headerShown: false,
            tabBarIcon: ({ focused }) => (
            <TabIcon focused={focused} icon={icons.store} title="Market" />
          ),
          }}
        />
      </Tabs>
    </View>
  );
};
export default _Layout;
