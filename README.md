# 🌱 Seikatsu

Seikatsu (生活) — meaning "life" in Japanese — is a personal growth and productivity application designed to help users track their daily activities, emotions, and habits.  
It provides insights, analytics, and an AI-powered behavioral analysis system to encourage a balanced and fulfilling lifestyle.  

---

## ✨ Features

- 📊 **Daily Journaling** — Log activities, achievements, mistakes, nutrition, and sleep.
- 💡 **AI Analysis** — NLP-powered insights on habits, mood, and performance.
- 🎭 **Emotion Tracking** — Record emotions like Happy, Sad, Angry, Scared, Confused.
- 🏆 **Gamified XP System** — Earn XP by completing milestones in categories:
  - Strength  
  - Learning  
  - Relationship  
  - Spirituality  
  - Career  
  - Sleep  
  - Nutrition
- 🛒 **Marketplace** — Unlock custom themes using earned XP.
- 📈 **Insights Dashboard** — Animated progress bars, charts, and visual reports.
- 🔔 **Reminders & Notifications** — Stay consistent with your goals.

---

## 🛠️ Tech Stack

### Frontend (Mobile App)
- ⚛️ React Native (with Expo)
- 🎨 NativeWind (Tailwind for React Native)
- 📱 Expo Router (navigation)
- 📊 Recharts & Animated APIs (for charts and progress bars)

### Backend
- 🚀 FastAPI (Python)
- 🤖 NLP for text analysis & insights
- 🗄️ PostgreSQL (database)

---

## 📂 Project Structure

```bash
seikatsu/
│
├── app/                  # Expo Router structure
│   ├── (tabs)/           # Bottom navigation tabs
│   │   ├── index.tsx     # Home screen
│   │   ├── journal.tsx   # Journal screen
│   │   ├── insights.tsx  # Insights screen
│   │   └── market.tsx    # Marketplace screen
│   │
│   └── _layout.tsx       # Root layout for navigation
│
├── components/           # Reusable UI components
│   ├── HeaderBar.tsx     # Top header bar
│   └── ...
│
├── constants/            # Assets, icons, and images
│
├── backend/              # FastAPI backend
│   ├── main.py           # Entry point
│   ├── models.py         # Database models
│   ├── routes/           # API endpoints
│   └── nlp/              # Text processing pipeline
│
└── README.md             # Project documentation


🚀 Getting Started
Prerequisites

Node.js & npm

Expo CLI

Python 3.10+

PostgreSQL

Setup
# Clone the repository
git clone https://github.com/<your-username>/seikatsu.git
cd seikatsu

# Install frontend dependencies
npm install

# Start Expo project
npx expo start


Backend setup:

cd backend
pip install -r requirements.txt
uvicorn main:app --reload

📊 Screenshots (Preview)

(Add screenshots/gifs of your app here once UI is built)

📅 Roadmap

 Basic UI with Expo + Tailwind

 Bottom navigation tabs

 HeaderBar with notifications/settings

 Journal entry & storage

 AI analysis integration

 Gamified XP + Marketplace themes

 Data export (CSV/PDF)

🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to fork this repo and submit a PR.

📜 License

MIT License © 2025 Zayhn Ahmed
