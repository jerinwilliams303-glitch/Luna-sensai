🌙 Luna Sensai — Menstrual Health & Wellness Companion

Luna Sensai is a desktop application built using Python and Tkinter that helps users track menstrual cycles, predict symptoms using machine learning, log daily wellness data, access guided meditations, set reminders, and chat with an AI companion powered by Google Gemini.

Designed to be a supportive, empathetic, and intelligent companion, Luna Sensai helps users better understand their health and emotional well-being. 🌸💖

✨ Features
🌼 Menstrual Cycle Tracking

Log daily symptoms (mood, cramps, sleep, meals, stress, notes).

Track cycle phases and view insights.

🤖 AI Companion (Luna)

Chat with a warm, friendly AI assistant.

Supports emotional health and wellbeing.

Uses Google Gemini (API key required).

📊 Machine Learning Predictions

Predicts mood patterns

Predicts cramp severity

Trains ML models using your datasets

Uses RandomForest classifiers

📅 Reminders & Notifications

Set personal reminders

Wellness self-care alerts

Medication & hydration reminders

🧘 Guided Meditations

Calming mindfulness sessions

Helps users reduce stress & anxiety

📈 Data Visualizations

Graphs for mood, stress, sleep, cycle data

Weekly and monthly insights

🗃 Local Database Storage

All data stored securely in SQLite

Works offline

No cloud dependencies except AI

🛠 Tech Stack

Python 3.x

Tkinter → GUI

SQLite → Database

scikit-learn → ML models

Matplotlib → Graphs

Pandas / NumPy → Data processing

Google Generative AI → AI Companion

📦 Installation
1. Clone the repository
git clone https://github.com/jerinwilliams303-glitch/luna-sensai.git
cd luna-sensai

2. Create a virtual environment
python -m venv venv

Activate:

Windows

venv\Scripts\activate


Mac/Linux

source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

🔐 Environment Variables

Create a .env file (not included in repo):

GENAI_API_KEY=your_google_gemini_api_key

Ensure .env is included in .gitignore.

▶️ Run the Application
python app.py

📁 Project Structure
luna-sensai/
│── app.py
│── ai_companion.py
│── ml_models.py
│── ui_components.py
│── database.py
│── requirements.txt
│── README.md
│── .gitignore
│── .env.example
│── assets/
│── data/

📝 License

This project is licensed under the MIT License.
See the LICENSE file for details.

💡 Future Enhancements

Dark mode UI

More AI features (emotion detection, journaling suggestions)

Cloud backup of user logs

Mobile version using Flutter/Kivy

Multi-language support

Voice-based AI companion

💖 Contributors

Jerin Williams

