import {
  Activity,
  Bell,
  BookOpen,
  Brain,
  Camera,
  ChevronRight,
  Cloud,
  Download,
  Eye,
  FileText,
  Globe,
  HelpCircle,
  Info,
  Link,
  Loader,
  Lock,
  LogOut,
  Mail,
  MessageCircle,
  Palette,
  Smartphone,
  Target,
  Trash2,
  Type,
  User
} from 'lucide-react';
import React, { useEffect, useState } from 'react';

// Color palette constants
const COLORS = {
  primary: '#371931',
  secondary: '#FECD8A',
  light100: '#F8E9D2',
  light200: '#F3D8BE',
  light300: '#EBD1C1',
  dark100: '#2C1127',
  dark200: '#1F0B19',
  dark300: '#14060F',
  accent: '#B37BA4',
  success: '#A8FFCB',
  alert: '#FF8080',
  info: '#89CFF0',
};

// Settings configuration with backend integration points
const SETTINGS_CONFIG = {
  'profile': {
    title: 'Profile & Account',
    items: [
      { 
        id: 'edit-profile', 
        label: 'Edit Profile', 
        icon: User, 
        route: '/profile/edit',
        requiresAuth: true,
        apiEndpoint: '/api/user/profile'
      },
      { 
        id: 'change-email', 
        label: 'Change Email', 
        icon: Mail, 
        route: '/profile/email',
        requiresAuth: true,
        apiEndpoint: '/api/user/email'
      },
      { 
        id: 'change-password', 
        label: 'Change Password', 
        icon: Lock, 
        route: '/profile/password',
        requiresAuth: true,
        apiEndpoint: '/api/user/password'
      },
      { 
        id: 'linked-accounts', 
        label: 'Linked Accounts', 
        icon: Link, 
        route: '/profile/accounts',
        requiresAuth: true,
        apiEndpoint: '/api/user/linked-accounts'
      },
    ]
  },
  'ai': {
    title: 'AI & Personalization',
    items: [
      { 
        id: 'ai-preferences', 
        label: 'AI Preferences', 
        icon: Brain, 
        route: '/settings/ai',
        requiresAuth: true,
        apiEndpoint: '/api/user/ai-preferences'
      },
      { 
        id: 'language-region', 
        label: 'Language & Region', 
        icon: Globe, 
        route: '/settings/language',
        requiresAuth: false,
        apiEndpoint: '/api/user/preferences'
      },
      { 
        id: 'notifications', 
        label: 'Notifications', 
        icon: Bell, 
        route: '/settings/notifications',
        requiresAuth: true,
        apiEndpoint: '/api/user/notifications'
      },
    ]
  },
  'growth': {
    title: 'Growth & Tracking',
    items: [
      { 
        id: 'habit-settings', 
        label: 'Habit Settings', 
        icon: Target, 
        route: '/settings/habits',
        requiresAuth: true,
        apiEndpoint: '/api/user/habit-settings'
      },
      { 
        id: 'journaling-settings', 
        label: 'Journaling Settings', 
        icon: BookOpen, 
        route: '/settings/journaling',
        requiresAuth: true,
        apiEndpoint: '/api/user/journal-settings'
      },
      { 
        id: 'data-sync', 
        label: 'Data Sync', 
        icon: Cloud, 
        route: '/settings/sync',
        requiresAuth: true,
        apiEndpoint: '/api/user/sync-settings'
      },
    ]
  },
  'privacy': {
    title: 'Privacy & Security',
    items: [
      { 
        id: 'permissions', 
        label: 'Manage Permissions', 
        icon: Camera, 
        route: '/settings/permissions',
        requiresAuth: true,
        apiEndpoint: '/api/user/permissions'
      },
      { 
        id: 'privacy-controls', 
        label: 'Privacy Controls', 
        icon: Eye, 
        route: '/settings/privacy',
        requiresAuth: true,
        apiEndpoint: '/api/user/privacy'
      },
      { 
        id: 'app-lock', 
        label: 'App Lock', 
        icon: Smartphone, 
        route: '/settings/security',
        requiresAuth: true,
        apiEndpoint: '/api/user/security'
      },
    ]
  },
  'integrations': {
    title: 'Integrations',
    items: [
      { 
        id: 'health-apps', 
        label: 'Health Apps', 
        icon: Activity, 
        route: '/settings/integrations/health',
        requiresAuth: true,
        apiEndpoint: '/api/integrations/health'
      },
      { 
        id: 'api-export', 
        label: 'API & Export', 
        icon: Download, 
        route: '/settings/export',
        requiresAuth: true,
        apiEndpoint: '/api/user/export'
      },
    ]
  },
  'appearance': {
    title: 'Appearance',
    items: [
      { 
        id: 'theme', 
        label: 'Theme', 
        icon: Palette, 
        route: '/settings/theme',
        requiresAuth: false,
        apiEndpoint: '/api/user/preferences'
      },
      { 
        id: 'accessibility', 
        label: 'Font & Accessibility', 
        icon: Type, 
        route: '/settings/accessibility',
        requiresAuth: false,
        apiEndpoint: '/api/user/preferences'
      },
    ]
  },
  'support': {
    title: 'Support & About',
    items: [
      { 
        id: 'help', 
        label: 'Help Center / FAQs', 
        icon: HelpCircle, 
        route: '/help',
        requiresAuth: false,
        external: true
      },
      { 
        id: 'contact', 
        label: 'Contact Support', 
        icon: MessageCircle, 
        route: '/support',
        requiresAuth: false,
        external: true
      },
      { 
        id: 'legal', 
        label: 'Terms & Privacy Policy', 
        icon: FileText, 
        route: '/legal',
        requiresAuth: false,
        external: true
      },
      { 
        id: 'version', 
        label: 'App Version', 
        icon: Info, 
        route: '/settings/about',
        requiresAuth: false,
        showValue: true
      },
    ]
  },
  'account': {
    title: 'Account Actions',
    items: [
      { 
        id: 'logout', 
        label: 'Log Out', 
        icon: LogOut, 
        isDestructive: true,
        requiresAuth: true,
        apiEndpoint: '/api/auth/logout',
        confirmationRequired: true
      },
      { 
        id: 'delete-account', 
        label: 'Delete Account', 
        icon: Trash2, 
        isDestructive: true,
        requiresAuth: true,
        apiEndpoint: '/api/user/delete',
        confirmationRequired: true,
        dangerLevel: 'high'
      },
    ]
  }
};

const SettingsPage = () => {
  // State management for backend integration
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [appVersion, setAppVersion] = useState('1.0.0');
  const [isAuthenticated, setIsAuthenticated] = useState(true); // Mock auth state

  // Simulate data fetching
  useEffect(() => {
    fetchUserData();
    fetchAppVersion();
  }, []);

  // Mock API functions - replace with your actual API calls
  const fetchUserData = async () => {
    try {
      setLoading(true);
      // const response = await api.get('/api/user/profile');
      // setUser(response.data);
      
      // Mock data
      setUser({
        id: '12345',
        email: 'user@example.com',
        name: 'John Doe'
      });
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAppVersion = async () => {
    try {
      // const version = await getAppVersion(); // Your version fetching logic
      setAppVersion('1.0.0');
    } catch (error) {
      console.error('Failed to fetch app version:', error);
    }
  };

  // Navigation handler - integrate with your navigation system
  const handleNavigation = (item) => {
    if (item.external) {
      // Handle external links (web browser, external apps)
      window.open(item.route, '_blank');
      return;
    }

    if (item.requiresAuth && !isAuthenticated) {
      // Redirect to login
      console.log('Redirecting to login...');
      return;
    }

    // Navigate using your navigation system (React Navigation, etc.)
    console.log(`Navigating to: ${item.route}`);
    // navigation.navigate(item.route);
  };

  // API call handler
  const handleApiCall = async (item) => {
    if (!item.apiEndpoint) return;

    try {
      setLoading(true);
      
      if (item.confirmationRequired) {
        const confirmed = window.confirm(`Are you sure you want to ${item.label.toLowerCase()}?`);
        if (!confirmed) return;
      }

      // Make API call based on the item type
      if (item.id === 'logout') {
        // await api.post('/api/auth/logout');
        console.log('Logging out...');
        setIsAuthenticated(false);
        // navigation.navigate('Login');
      } else if (item.id === 'delete-account') {
        // await api.delete('/api/user/delete');
        console.log('Deleting account...');
        setIsAuthenticated(false);
        // navigation.navigate('Welcome');
      } else {
        // For other API calls, navigate to the settings page
        handleNavigation(item);
      }
    } catch (error) {
      console.error(`API call failed for ${item.id}:`, error);
      // Handle error (show toast, alert, etc.)
    } finally {
      setLoading(false);
    }
  };

  // Main item press handler
  const handleItemPress = (item) => {
    if (item.apiEndpoint && (item.id === 'logout' || item.id === 'delete-account')) {
      handleApiCall(item);
    } else {
      handleNavigation(item);
    }
  };

  const SettingItem = ({ item }) => (
    <button 
      onClick={() => handleItemPress(item)}
      className="w-full flex items-center justify-between p-4 text-left transition-colors"
      style={{
        backgroundColor: item.isDestructive ? 'rgba(255, 128, 128, 0.1)' : COLORS.light100
      }}
      onMouseEnter={(e) => {
        e.target.style.backgroundColor = item.isDestructive ? 'rgba(255, 128, 128, 0.2)' : 'rgba(248, 233, 210, 0.7)';
      }}
      onMouseLeave={(e) => {
        e.target.style.backgroundColor = item.isDestructive ? 'rgba(255, 128, 128, 0.1)' : COLORS.light100;
      }}
      disabled={loading || (item.requiresAuth && !isAuthenticated)}
    >
      <div className="flex items-center flex-1">
        <item.icon 
          size={20} 
          className="mr-3"
          style={{color: item.isDestructive ? COLORS.alert : COLORS.primary}}
        />
        <span 
          className={`text-base ${item.isDestructive ? 'font-medium' : ''}`}
          style={{color: item.isDestructive ? COLORS.alert : COLORS.dark200}}
        >
          {item.label}
        </span>
        {item.showValue && item.id === 'version' && (
          <span className="ml-2 text-sm" style={{color: COLORS.accent}}>
            v{appVersion}
          </span>
        )}
      </div>
      {loading && item.id === 'logout' ? (
        <Loader size={16} className="animate-spin" style={{color: COLORS.accent}} />
      ) : (
        <ChevronRight size={16} style={{color: COLORS.accent}} />
      )}
    </button>
  );

  const SettingSection = ({ sectionKey, section }) => (
    <div className="mb-6">
      <h3 className="text-sm font-bold uppercase tracking-wide mb-3 px-4" style={{color: COLORS.accent}}>
        {section.title}
      </h3>
      <div className="rounded-xl shadow-sm mx-4 overflow-hidden border" style={{backgroundColor: COLORS.light200, borderColor: COLORS.light300}}>
        {section.items.map((item, index) => (
          <div key={item.id}>
            <SettingItem item={item} />
            {index < section.items.length - 1 && (
              <div className="h-px ml-12" style={{backgroundColor: COLORS.light300}} />
            )}
          </div>
        ))}
      </div>
    </div>
  );

  if (loading && !user) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{backgroundColor: COLORS.light100}}>
        <Loader size={32} className="animate-spin" style={{color: COLORS.primary}} />
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{backgroundColor: COLORS.light100}}>
      {/* Header */}
      <div className="px-4 py-6" style={{backgroundColor: COLORS.primary}}>
        <h1 className="text-xl font-semibold" style={{color: COLORS.secondary}}>Settings</h1>
        {user && (
          <p className="text-sm mt-1 opacity-80" style={{color: COLORS.secondary}}>
            {user.name} • {user.email}
          </p>
        )}
      </div>
      
      <div className="overflow-y-auto">
        <div className="py-6">
          {Object.entries(SETTINGS_CONFIG).map(([key, section]) => (
            <SettingSection key={key} sectionKey={key} section={section} />
          ))}
        </div>
        
        {/* Bottom spacing */}
        <div className="h-8" />
      </div>
    </div>
  );
};

export default SettingsPage;