import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from tkinter import messagebox
import os # Import the os module

def train_mood_cramp_models():
    """
    Trains the mood and cramp prediction models from Dataset_2.csv.
    Returns the trained models and the label encoder.
    """
    try:
        # --- THE FIX ---
        # Get the absolute path to the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Join the directory path with the filename to create a full, reliable path
        file_path = os.path.join(script_dir, 'Dataset_2.csv')
        
        # Read the CSV using the full path
        df = pd.read_csv(file_path)
        # --- END OF FIX ---
        
        df['Symptoms_Cramps'] = df['Symptoms'].apply(lambda x: 1 if 'Cramps' in x else 0)
        symptom_to_mood = {'Headache': 'Stressed', 'Fatigue': 'Tired', 'Bloating': 'Neutral', 'Cramps': 'Sad', 'Mood Swings': 'Unstable'}
        df['Mood'] = df['Symptoms'].map(symptom_to_mood).fillna('Neutral')
        
        features = ['Age', 'BMI', 'Stress Level', 'Sleep Hours']
        X = df[features]
        y_mood = df['Mood']
        y_cramps = df['Symptoms_Cramps']
        
        le_mood = LabelEncoder()
        y_mood_encoded = le_mood.fit_transform(y_mood)
        
        mood_model = RandomForestClassifier(n_estimators=100, random_state=42)
        mood_model.fit(X, y_mood_encoded)
        
        cramp_model = RandomForestClassifier(n_estimators=100, random_state=42)
        cramp_model.fit(X, y_cramps)
        
        return mood_model, cramp_model, {'mood': le_mood}
        
    except FileNotFoundError:
        messagebox.showerror("Error", "Dataset_2.csv not found in the application folder. Forecasting will be disabled.")
        return None, None, None
    except Exception as e:
        messagebox.showerror("Model Training Error", f"Could not train models. Error: {e}")
        return None, None, None