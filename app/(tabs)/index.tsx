import HomeTabs from "@/components/home/HomeTabs";
import { ScrollView, View } from "react-native";

export default function Index() {
  return (
    <View className="flex-1 bg-primary">

      {/* Scrollable content */}
      <ScrollView
        className="flex-1 px-5"
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ minHeight: "100%", paddingTop: 100 }}
      >
        
        <HomeTabs />

       
      </ScrollView>
    </View>
  );
}
