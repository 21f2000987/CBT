# TCS iON Style CBT Exam Engine (Foundation)

A comprehensive, offline-first Computer Based Test (CBT) platform built with Flask, mimicking the TCS iON Foundation exam engine.

## Features
- **TCS iON UI**: Authentic exam interface, question palette, and navigation.
- **Offline-First**: PWA support with local caching and encryption.
- **Security**: Restricted frontend (disabled right-click, F12), tab-switch detection, and full-screen proctoring.
- **Admin Control**: Teacher-controlled exam activation, question management, and analytics.
- **AI Integration**: Dynamic question generation using NCERT chapters (Ollama/Mistral).
- **Adaptive Testing**: Difficulty adjustment based on performance.
- **Multi-lingual**: Support for English, Hindi, and Sanskrit with on-screen keyboard.

## Installation & Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in a `.env` file (SECRET_KEY, DATABASE_URL).
4. Run the application: `python run.py`

## Deployment
Ready for deployment on **Vercel**.
