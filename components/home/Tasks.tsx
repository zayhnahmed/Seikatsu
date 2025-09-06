import { useState } from "react";
import { Animated, Dimensions, Platform, ScrollView, Text, TextInput, TouchableOpacity, View } from "react-native";

const { width } = Dimensions.get('window');

interface Task {
  id: string;
  title: string;
  completed: boolean;
  priority: 1 | 2 | 3 | 4;
}

interface PriorityConfig {
  label: string;
  color: string;
  bgColor: string;
  textColor: string;
}

export default function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([
    { id: "1", title: "Finish workout", completed: false, priority: 1 },
    { id: "2", title: "Read 10 pages", completed: true, priority: 3 },
    { id: "3", title: "Work on Seikatsu UI", completed: false, priority: 2 },
  ]);
  const [newTask, setNewTask] = useState<string>("");
  const [showPrioritySelector, setShowPrioritySelector] = useState<boolean>(false);
  const [selectedPriority, setSelectedPriority] = useState<1 | 2 | 3 | 4>(3);
  const [slideAnim] = useState(new Animated.Value(0));
  const [swipeAnimations, setSwipeAnimations] = useState<Record<string, Animated.Value>>({});

  const priorityConfig: Record<1 | 2 | 3 | 4, PriorityConfig> = {
    1: { 
      label: "High Priority", 
      color: "#ef4444", 
      bgColor: "#fef2f2",
      textColor: "#991b1b"
    },
    2: { 
      label: "Medium Priority", 
      color: "#22c55e", 
      bgColor: "#f0fdf4",
      textColor: "#166534"
    },
    3: { 
      label: "Average Priority", 
      color: "#3b82f6", 
      bgColor: "#eff6ff",
      textColor: "#1e40af"
    },
    4: { 
      label: "Low Priority", 
      color: "#6b7280", 
      bgColor: "#f9fafb",
      textColor: "#374151"
    }
  };

  const getSwipeAnimation = (taskId: string) => {
    if (!swipeAnimations[taskId]) {
      setSwipeAnimations(prev => ({
        ...prev,
        [taskId]: new Animated.Value(0)
      }));
      return new Animated.Value(0);
    }
    return swipeAnimations[taskId];
  };

  const handleSwipe = (taskId: string, translationX: number) => {
    const swipeAnim = getSwipeAnimation(taskId);
    
    // Only allow left swipe (negative values)
    const clampedTranslation = Math.min(0, Math.max(-80, translationX));
    swipeAnim.setValue(clampedTranslation);
  };

  const handleSwipeEnd = (taskId: string, translationX: number, velocityX: number) => {
    const swipeAnim = getSwipeAnimation(taskId);
    
    // Determine if we should snap to open or closed position
    const shouldOpen = translationX < -40 || velocityX < -500;
    const targetValue = shouldOpen ? -80 : 0;
    
    Animated.spring(swipeAnim, {
      toValue: targetValue,
      useNativeDriver: false,
      tension: 100,
      friction: 8
    }).start();
  };

  const closeSwipe = (taskId: string) => {
    const swipeAnim = getSwipeAnimation(taskId);
    Animated.spring(swipeAnim, {
      toValue: 0,
      useNativeDriver: false,
      tension: 100,
      friction: 8
    }).start();
  };

  const deleteTask = (id: string) => {
    setTasks((prev) => prev.filter((task) => task.id !== id));
    // Clean up animation for this task
    setSwipeAnimations(prev => {
      const { [id]: removed, ...rest } = prev;
      return rest;
    });
  };

  const toggleTask = (id: string) => {
    setTasks((prev) =>
      prev.map((task) =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const addTask = () => {
    if (!newTask.trim()) return;
    setTasks((prev) => [
      ...prev,
      { 
        id: Date.now().toString(), 
        title: newTask, 
        completed: false,
        priority: selectedPriority
      },
    ]);
    setNewTask("");
    closePrioritySelector();
    setSelectedPriority(3);
  };

  const handleAddClick = () => {
    if (!newTask.trim()) return;
    openPrioritySelector();
  };

  const openPrioritySelector = () => {
    setShowPrioritySelector(true);
    Animated.timing(slideAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: false,
    }).start();
  };

  const closePrioritySelector = () => {
    Animated.timing(slideAnim, {
      toValue: 0,
      duration: 300,
      useNativeDriver: false,
    }).start(() => {
      setShowPrioritySelector(false);
    });
  };

  const handlePrioritySelect = (priority: 1 | 2 | 3 | 4) => {
    setSelectedPriority(priority);
  };

  const getPriorityStyles = (priority: 1 | 2 | 3 | 4) => {
    const config = priorityConfig[priority];
    return {
      borderColor: config.color,
      indicatorColor: config.color
    };
  };

  const animatedHeight = slideAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, 140],
  });

  const renderTask = ({ item }: { item: Task }) => {
    const priorityStyles = getPriorityStyles(item.priority);
    const swipeAnim = getSwipeAnimation(item.id);
    
    return (
      <View style={{ marginBottom: 12, position: 'relative' }}>
        {/* Delete Button Background */}
        <View style={{
          position: 'absolute',
          right: 0,
          top: 0,
          bottom: 0,
          width: 80,
          backgroundColor: '#ef4444',
          borderRadius: 16,
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1
        }}>
          <TouchableOpacity
            onPress={() => deleteTask(item.id)}
            style={{
              width: '100%',
              height: '100%',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            activeOpacity={0.8}
          >
            <Text style={{
              color: '#FFFFFF',
              fontSize: 18,
              fontWeight: 'bold'
            }}>
              Delete
            </Text>
          </TouchableOpacity>
        </View>

        {/* Main Task Content */}
        <Animated.View
          style={{
            transform: [{ translateX: swipeAnim }],
            backgroundColor: item.completed ? '#2C1127' : '#371931',
            borderRadius: 16,
            padding: 16,
            borderLeftWidth: 4,
            borderLeftColor: priorityStyles.borderColor,
            borderWidth: 1,
            borderColor: '#452347',
            opacity: item.completed ? 0.7 : 1,
            zIndex: 2
          }}
          {...(Platform.OS === 'web' ? {
            onTouchStart: (e: any) => {
              const touch = e.touches[0];
              const startX = touch.clientX;
              let currentX = startX;
              
              const handleTouchMove = (moveEvent: any) => {
                const moveTouch = moveEvent.touches[0];
                currentX = moveTouch.clientX;
                const translationX = currentX - startX;
                handleSwipe(item.id, translationX);
              };
              
              const handleTouchEnd = () => {
                const translationX = currentX - startX;
                const velocityX = 0; // Web doesn't have velocity easily available
                handleSwipeEnd(item.id, translationX, velocityX);
                document.removeEventListener('touchmove', handleTouchMove);
                document.removeEventListener('touchend', handleTouchEnd);
              };
              
              document.addEventListener('touchmove', handleTouchMove);
              document.addEventListener('touchend', handleTouchEnd);
            }
          } : {})}
        >
          <TouchableOpacity
            onPress={() => toggleTask(item.id)}
            style={{
              flexDirection: 'row', 
              alignItems: 'center', 
              justifyContent: 'space-between'
            }}
            activeOpacity={0.8}
          >
            <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
              {/* Priority Indicator */}
              <View 
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: 6,
                  backgroundColor: priorityStyles.indicatorColor,
                  marginRight: 12
                }}
              />
              
              {/* Task Content */}
              <View style={{ flex: 1 }}>
                <Text
                  style={{
                    fontSize: 16,
                    fontWeight: '500',
                    color: item.completed ? '#B37BA4' : '#FFFFFF',
                    textDecorationLine: item.completed ? 'line-through' : 'none',
                  }}
                >
                  {item.title}
                </Text>
                <Text style={{
                  fontSize: 12,
                  color: '#B37BA4',
                  marginTop: 4
                }}>
                  {priorityConfig[item.priority].label}
                </Text>
              </View>
            </View>

            {/* Completion Status */}
            <View
              style={{
                width: 24,
                height: 24,
                borderRadius: 12,
                backgroundColor: item.completed ? '#A8FFCB' : 'transparent',
                borderWidth: item.completed ? 0 : 2,
                borderColor: '#B37BA4',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {item.completed && (
                <Text style={{ color: '#371931', fontSize: 14, fontWeight: 'bold' }}>✓</Text>
              )}
            </View>
          </TouchableOpacity>
        </Animated.View>
      </View>
    );
  };

  const renderHeader = () => (
    <View>
      {/* Header */}
      <View style={{ marginBottom: 24 }}>
        <Text style={{ fontSize: 28, fontWeight: 'bold', color: '#FFFFFF', marginBottom: 8 }}>
          Tasks
        </Text>
        <Text style={{ color: '#B37BA4', fontSize: 16 }}>
          {tasks.filter(t => !t.completed).length} pending tasks
        </Text>
      </View>

      {/* Input Field */}
      <View style={{
        backgroundColor: '#2C1127',
        borderRadius: 20,
        padding: 16,
        marginBottom: 24,
        borderWidth: 1,
        borderColor: '#371931'
      }}>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <TextInput
            value={newTask}
            onChangeText={setNewTask}
            placeholder="Add a new task..."
            placeholderTextColor="#B37BA4"
            style={{
              flex: 1,
              color: '#FFFFFF',
              fontSize: 16,
              marginRight: 12
            }}
            onSubmitEditing={handleAddClick}
          />
          <TouchableOpacity 
            onPress={handleAddClick}
            disabled={!newTask.trim()}
            style={{
              backgroundColor: newTask.trim() ? '#FECD8A' : '#B37BA4',
              paddingHorizontal: 20,
              paddingVertical: 10,
              borderRadius: 12,
              opacity: newTask.trim() ? 1 : 0.5
            }}
            activeOpacity={0.8}
          >
            <Text style={{
              color: '#371931',
              fontWeight: '600',
              fontSize: 14
            }}>
              Add
            </Text>
          </TouchableOpacity>
        </View>

        {/* Animated Priority Selector */}
        {showPrioritySelector && (
          <Animated.View style={{
            height: animatedHeight,
            overflow: 'hidden'
          }}>
            <View style={{
              borderTopWidth: 1,
              borderTopColor: '#371931',
              paddingTop: 16,
              marginTop: 16
            }}>
              <Text style={{
                color: '#B37BA4',
                fontSize: 14,
                marginBottom: 12
              }}>
                Select Priority:
              </Text>
              
              <View style={{ flexDirection: 'row', marginBottom: 16 }}>
                {Object.entries(priorityConfig).map(([priority, config]) => (
                  <TouchableOpacity
                    key={priority}
                    onPress={() => handlePrioritySelect(parseInt(priority) as 1 | 2 | 3 | 4)}
                    style={{
                      flex: 1,
                      padding: 8,
                      marginHorizontal: 2,
                      borderRadius: 8,
                      borderWidth: 2,
                      borderColor: selectedPriority === parseInt(priority) ? config.color : '#371931',
                      backgroundColor: selectedPriority === parseInt(priority) ? config.color : '#371931',
                      alignItems: 'center'
                    }}
                    activeOpacity={0.8}
                  >
                    <Text style={{
                      fontSize: 12,
                      fontWeight: '600',
                      color: selectedPriority === parseInt(priority) ? '#FFFFFF' : '#B37BA4'
                    }}>
                      {priority}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              <View style={{ flexDirection: 'row' }}>
                <TouchableOpacity
                  onPress={addTask}
                  style={{
                    flex: 1,
                    backgroundColor: '#FECD8A',
                    paddingVertical: 12,
                    borderRadius: 12,
                    alignItems: 'center',
                    marginRight: 8
                  }}
                  activeOpacity={0.8}
                >
                  <Text style={{
                    color: '#371931',
                    fontWeight: '600',
                    fontSize: 14
                  }}>
                    Create Task
                  </Text>
                </TouchableOpacity>
                
                <TouchableOpacity
                  onPress={closePrioritySelector}
                  style={{
                    paddingHorizontal: 16,
                    paddingVertical: 12,
                    borderRadius: 12,
                    alignItems: 'center'
                  }}
                  activeOpacity={0.8}
                >
                  <Text style={{
                    color: '#B37BA4',
                    fontSize: 14
                  }}>
                    Cancel
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          </Animated.View>
        )}
      </View>
    </View>
  );

  const renderFooter = () => {
    if (tasks.length === 0) {
      return (
        <View style={{
          alignItems: 'center',
          paddingVertical: 48
        }}>
          <Text style={{ fontSize: 48, marginBottom: 16 }}>📝</Text>
          <Text style={{
            fontSize: 20,
            fontWeight: '600',
            color: '#FFFFFF',
            marginBottom: 8
          }}>
            No tasks yet
          </Text>
          <Text style={{
            color: '#B37BA4',
            textAlign: 'center'
          }}>
            Add your first task to get started!
          </Text>
        </View>
      );
    }

    return (
      <View style={{
        backgroundColor: '#2C1127',
        borderRadius: 16,
        padding: 16,
        marginTop: 32,
        marginBottom: 20,
        borderWidth: 1,
        borderColor: '#371931'
      }}>
        <View style={{
          flexDirection: 'row',
          justifyContent: 'space-around'
        }}>
          <View style={{ alignItems: 'center' }}>
            <Text style={{
              fontSize: 24,
              fontWeight: 'bold',
              color: '#FECD8A'
            }}>
              {tasks.filter(t => t.completed).length}
            </Text>
            <Text style={{
              fontSize: 12,
              color: '#B37BA4'
            }}>
              Completed
            </Text>
          </View>
          
          <View style={{ alignItems: 'center' }}>
            <Text style={{
              fontSize: 24,
              fontWeight: 'bold',
              color: '#89CFF0'
            }}>
              {tasks.filter(t => !t.completed).length}
            </Text>
            <Text style={{
              fontSize: 12,
              color: '#B37BA4'
            }}>
              Pending
            </Text>
          </View>
          
          <View style={{ alignItems: 'center' }}>
            <Text style={{
              fontSize: 24,
              fontWeight: 'bold',
              color: '#B37BA4'
            }}>
              {tasks.length}
            </Text>
            <Text style={{
              fontSize: 12,
              color: '#B37BA4'
            }}>
              Total
            </Text>
          </View>
        </View>
      </View>
    );
  };

  return (
    <View style={{
      flex: 1,
      backgroundColor: '#1F0B19',
    }}>
      <ScrollView
        style={{
          flex: 1,
        }}
        contentContainerStyle={{
          paddingHorizontal: 16,
          paddingTop: 16,
          paddingBottom: 40,
        }}
        showsVerticalScrollIndicator={false}
      >
        {renderHeader()}
        
        {tasks.map((item) => (
          <View key={item.id}>
            {renderTask({ item })}
          </View>
        ))}
        
        {renderFooter()}
      </ScrollView>
    </View>
  );
}