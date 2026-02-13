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
4. Run the application: `python index.py`

## VS Code Setup
- Open the project folder in VS Code.
- Install the **Python** extension.
- Select your Python interpreter (Ctrl+Shift+P -> "Python: Select Interpreter").
- Go to the "Run and Debug" tab (Ctrl+Shift+D).
- Select **Python: Flask** and press F5 to start debugging.

## Bundling for PC (Standalone EXE)
To create a single-file executable for offline use on individual PCs:
1. Install PyInstaller: `pip install pyinstaller`
2. Run the bundling script: `python build_exe.py`
3. The standalone application will be generated in the `dist` folder.
4. Copy the `.exe` to any PC to install/run the exam engine offline.

## Deployment
Ready for deployment on **Vercel** (using `index.py`).
