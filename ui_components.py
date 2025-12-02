import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkcalendar import DateEntry
import pandas as pd
from datetime import datetime, timedelta
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import random # Needed for mindfulness moments

import database as db
import ai_companion

# --- Meditation Content ---
GUIDED_MEDITATIONS = {
    "Stress Relief": (
        "Stress Relief Meditation 😌",
        ("Find a comfortable position... Close your eyes gently.\n\n"
         "Take a slow, deep breath in... and exhale slowly...\n\n"
         "Bring awareness to your body... With each exhale, imagine tension melting away...\n\n"
         "Focus on your breath... If your mind wanders, gently guide it back...\n\n"
         "Imagine a warm, calming light filling your body...\n\n"
         "Rest in this calm awareness...\n\n"
         "When ready, slowly return your attention. Open your eyes. Carry this peace.")
    ),
    "Pain Management": (
        "Meditation for Cramp Relief 🌸",
        ("Find a comfortable position... Place a hand gently on your lower abdomen. Close your eyes.\n\n"
         "Begin with slow, deep breaths...\n\n"
         "Bring awareness to the discomfort without judgment...\n\n"
         "Imagine your breath flowing towards this area... Inhale warmth... Exhale tightness...\n\n"
         "Visualize a gentle, warm light soothing the area...\n\n"
         "Be kind to yourself. Send compassion...\n\n"
         "Continue breathing deeply...\n\n"
         "When ready, slowly return your awareness. Open your eyes gently.")
    )
}

MINDFULNESS_MOMENTS = [
    "Take 3 deep breaths. Notice the rise and fall of your chest or belly.",
    "Focus on one sound you can hear right now. Listen without judgment for 30 seconds.",
    "Look around and notice 5 things you can see. Acknowledge their color, shape, texture.",
    "Bring awareness to your feet on the floor. Feel the sensation of grounding.",
    "Slowly sip water. Notice the temperature and sensation as you swallow.",
    "Gently stretch your neck, rolling it slowly side to side.",
    "Notice the feeling of the air on your skin. Is it warm, cool, or neutral?"
]


# Each function now takes `app` as its first argument to access the main app instance

def create_dashboard_tab(app, frame):
    info_frame = ttk.Frame(frame, style='TFrame'); info_frame.pack(pady=20, padx=20, fill='x')
    app.dashboard_cycle_day = ttk.Label(info_frame, text="Cycle Day: --", font=('Helvetica', 14, 'bold'), style='TLabel'); app.dashboard_cycle_day.pack()
    app.dashboard_next_period = ttk.Label(info_frame, text="Next Period: Not Predicted", font=('Helvetica', 12), style='TLabel'); app.dashboard_next_period.pack()
    app.cycle_canvas = tk.Canvas(frame, width=300, height=300, bg=app.colors['bg'], highlightthickness=0); app.cycle_canvas.pack(pady=20)
    button_frame = ttk.Frame(frame, style='TFrame'); button_frame.pack(pady=10)
    log_button = ttk.Button(button_frame, text="📝 Log Today's Symptoms", command=lambda: app.notebook.select(app.logging_tab_index)); log_button.pack()
    reminders_frame = ttk.Frame(frame, style='TFrame', padding=10); reminders_frame.pack(pady=10, padx=20, fill='x')
    ttk.Label(reminders_frame, text="Today's Reminders ✨", font=('Helvetica', 12, 'bold')).pack()
    app.dashboard_reminders = ttk.Label(reminders_frame, text="No reminders for today.", justify='center'); app.dashboard_reminders.pack()
    update_dashboard(app)

def update_dashboard(app, last_date=None, cycle_length=28):
    app.cycle_canvas.delete("all"); app.cycle_canvas.create_oval(50, 50, 250, 250, outline=app.colors['primary'], width=10)
    if last_date:
        today = datetime.now().date(); current_cycle_day = (today - last_date).days + 1; current_cycle_day = max(1, current_cycle_day)
        next_period_date = last_date + timedelta(days=cycle_length); ovulation_day = next_period_date - timedelta(days=14); fertile_start = ovulation_day - timedelta(days=5)
        app.dashboard_cycle_day.config(text=f"Cycle Day: {current_cycle_day}"); app.dashboard_next_period.config(text=f"Predicted Next Period: {next_period_date.strftime('%b %d, %Y')}")
        period_start_angle = (360 / cycle_length) * (cycle_length - 1)
        app.cycle_canvas.create_arc(50, 50, 250, 250, start=period_start_angle, extent=(360/cycle_length)*5, style=tk.ARC, outline=app.colors['secondary'], width=10)
        fertile_start_day = (fertile_start - last_date).days if last_date else 0
        fertile_start_angle = (360 / cycle_length) * (fertile_start_day - 1); fertile_extent = (360 / cycle_length) * 6
        app.cycle_canvas.create_arc(50, 50, 250, 250, start=fertile_start_angle, extent=fertile_extent, style=tk.ARC, outline=app.colors['accent'], width=10)
        angle = (360 / cycle_length) * (current_cycle_day - 1); rad = math.radians(angle - 90); center_x, center_y, radius = 150, 150, 100
        x, y = center_x + radius * math.cos(rad), center_y + radius * math.sin(rad)
        app.cycle_canvas.create_oval(x-5, y-5, x+5, y+5, fill=app.colors['fg'], outline=app.colors['fg'])
    else:
        app.cycle_canvas.create_text(150, 150, text="Go to 'Period Prediction' tab\nto see your cycle wheel.", justify='center', font=('Helvetica', 10))
    today_str = datetime.now().strftime('%Y-%m-%d'); reminders = db.get_reminders_for_date(app.user_id, today_str)
    app.dashboard_reminders.config(text="\n".join(f"• {r}" for r in reminders) if reminders else "No reminders for today.")

def create_period_prediction_tab(app, frame):
    inner_frame = ttk.Frame(frame); inner_frame.pack(expand=True)
    ttk.Label(inner_frame, text="Last Period Date:").grid(row=0, column=0, padx=10, pady=10)
    app.last_period_date = DateEntry(inner_frame, width=12, background=app.colors['accent'], foreground='white', borderwidth=2); app.last_period_date.grid(row=0, column=1, padx=10, pady=10)
    ttk.Label(inner_frame, text="Average Cycle Length:").grid(row=1, column=0, padx=10, pady=10)
    app.avg_cycle_length = ttk.Entry(inner_frame); app.avg_cycle_length.grid(row=1, column=1, padx=10, pady=10)
    ttk.Button(inner_frame, text="🩸 Predict", command=lambda: predict_period(app)).grid(row=2, column=0, columnspan=2, pady=20)
    app.prediction_result = ttk.Label(inner_frame, text="", style='Result.TLabel'); app.prediction_result.grid(row=3, column=0, columnspan=2, pady=10)
    app.fertility_result = ttk.Label(inner_frame, text="", style='Result.TLabel', foreground=app.colors['secondary'], justify='center'); app.fertility_result.grid(row=4, column=0, columnspan=2, pady=5)

def predict_period(app):
    try:
        last_date, cycle_length = app.last_period_date.get_date(), int(app.avg_cycle_length.get())
        next_period_date = last_date + timedelta(days=cycle_length)
        app.prediction_result.config(text=f"Predicted Next Period Date: {next_period_date.strftime('%Y-%m-%d')}")
        ovulation_day = next_period_date - timedelta(days=14)
        fertile_window_start = ovulation_day - timedelta(days=5)
        app.fertility_result.config(text=f"Estimated Ovulation: {ovulation_day.strftime('%Y-%m-%d')}\nFertile Window: {fertile_window_start.strftime('%b %d')} - {ovulation_day.strftime('%b %d')}")
        update_dashboard(app, last_date, cycle_length)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for cycle length.")

def create_daily_logging_tab(app, frame):
    main_frame = ttk.Frame(frame); main_frame.pack(fill="both", expand=True); main_frame.grid_columnconfigure(1, weight=1)
    labels = ["🍽️ Breakfast:", "🥗 Lunch:", "🍝 Dinner:", "😊 Mood:", "😴 Sleep Hours:", "🧘 Stress Level:", "🏃 Physical Activity:", "💢 Cramp Intensity:", "🩺 PCOS:", "🦋 Thyroid:", "🏷️ Custom Tags:", "✍️ Notes:"]
    app.log_entries = {}
    for i, label_text in enumerate(labels): ttk.Label(main_frame, text=label_text).grid(row=i, column=0, padx=20, pady=7, sticky='nw')
    app.log_entries["Breakfast"], app.log_entries["Lunch"], app.log_entries["Dinner"] = ttk.Entry(main_frame), ttk.Entry(main_frame), ttk.Entry(main_frame)
    mood_values = ["😊 Happy", "🙂 Content", "😁 Joyful", "😂 Laughing", "😢 Sad", "😭 Crying", "😞 Disappointed", "😥 Gloomy", "😠 Angry", "😤 Frustrated", "😡 Annoyed", "😴 Tired", "😪 Sleepy", "😫 Exhausted", "😰 Anxious", "😨 Scared", "😱 Worried", "😐 Neutral", "😑 Calm", "😌 Relaxed", "😍 Energetic", "🤩 Motivated", "🥳 Excited"]
    app.log_entries["Mood"] = ttk.Combobox(main_frame, values=mood_values)
    app.log_entries["Sleep Hours"] = ttk.Entry(main_frame)
    app.log_entries["Stress Level"], app.log_entries["Cramp Intensity"] = ttk.Scale(main_frame, from_=1, to=10, orient='horizontal'), ttk.Scale(main_frame, from_=1, to=10, orient='horizontal')
    app.log_entries["Physical Activity"] = ttk.Combobox(main_frame, values=["Low", "Moderate", "High"])
    app.log_entries["PCOS"], app.log_entries["Thyroid"] = tk.BooleanVar(), tk.BooleanVar()
    app.log_entries["Custom Tags"] = ttk.Entry(main_frame)
    app.log_entries["Notes"] = scrolledtext.ScrolledText(main_frame, height=4, wrap=tk.WORD, font=('Helvetica', 10))
    for i, key in enumerate(["Breakfast", "Lunch", "Dinner", "Mood", "Sleep Hours", "Stress Level", "Physical Activity", "Cramp Intensity"]): app.log_entries[key].grid(row=i, column=1, padx=10, pady=7, sticky='ew')
    ttk.Checkbutton(main_frame, text="", variable=app.log_entries["PCOS"]).grid(row=8, column=1, padx=10, pady=7, sticky='w')
    ttk.Checkbutton(main_frame, text="", variable=app.log_entries["Thyroid"]).grid(row=9, column=1, padx=10, pady=7, sticky='w')
    app.log_entries["Custom Tags"].grid(row=10, column=1, padx=10, pady=7, sticky='ew')
    app.log_entries["Notes"].grid(row=11, column=1, padx=10, pady=7, sticky='ew')
    ttk.Button(main_frame, text="💾 Save Log", command=lambda: save_log(app)).grid(row=12, column=0, columnspan=2, pady=20)

def save_log(app):
    log_data = {'Date': datetime.now().strftime('%Y-%m-%d')}
    for key, widget in app.log_entries.items():
        value = widget.get("1.0", tk.END).strip() if isinstance(widget, scrolledtext.ScrolledText) else widget.get()
        if key == "Mood" and value: value = value.split(" ")[1] if len(value.split(" ")) > 1 else value
        log_data[key.split(" (")[0]] = value
    db.add_log(app.user_id, log_data)
    messagebox.showinfo("Success", "✨ Your log has been saved!")

def create_forecasting_tab(app, frame):
    inner_frame = ttk.Frame(frame); inner_frame.pack(expand=True, padx=20, pady=10)
    ttk.Label(inner_frame, text="Enter today's data for forecasting:", font=("Helvetica", 12)).grid(row=0, column=0, columnspan=3, pady=10)
    app.forecast_entries = {}
    labels = {"Age:": "Entry", "Weight (kg):": "Entry", "Height (cm):": "Entry", "Stress Level:": "Scale", "Sleep Hours:": "Scale"}
    for i, (text, widget_type) in enumerate(labels.items(), start=1):
        label = ttk.Label(inner_frame, text=text); label.grid(row=i, column=0, sticky='w', padx=5, pady=10)
        key = text.split(" ")[0].replace(":", "")
        if widget_type == "Entry":
            entry = ttk.Entry(inner_frame, width=10); entry.grid(row=i, column=1, sticky='ew', padx=5)
            app.forecast_entries[key] = entry
        else:
            value_label = ttk.Label(inner_frame, text="1", font=('Helvetica', 10, 'bold')); value_label.grid(row=i, column=2, padx=5)
            max_val = 12 if "Sleep" in text else 10
            scale = ttk.Scale(inner_frame, from_=1, to=max_val, orient='horizontal', command=lambda v, l=value_label: l.config(text=f"{float(v):.0f}")); scale.grid(row=i, column=1, sticky='ew', padx=5)
            app.forecast_entries[key] = scale
    inner_frame.grid_columnconfigure(1, weight=1)
    ttk.Button(inner_frame, text="🔮 Forecast Mood & Cramps", command=lambda: forecast_mood_cramps(app)).grid(row=len(labels)+1, column=0, columnspan=3, pady=20)
    app.forecast_result = ttk.Label(inner_frame, text="", style='Result.TLabel', justify='center'); app.forecast_result.grid(row=len(labels)+2, column=0, columnspan=3, pady=10)

def forecast_mood_cramps(app):
    if not app.mood_model or not app.cramp_model: messagebox.showerror("Error", "Models not trained."); return
    age_str, weight_str, height_str = app.forecast_entries['Age'].get(), app.forecast_entries['Weight'].get(), app.forecast_entries['Height'].get()
    if not all([age_str, weight_str, height_str]): messagebox.showerror("Input Error", "Fill in Age, Weight, Height."); return
    try:
        age, weight_kg, height_cm = float(age_str), float(weight_str), float(height_str)
        stress, sleep = float(app.forecast_entries['Stress'].get()), float(app.forecast_entries['Sleep'].get())
        if height_cm == 0: messagebox.showerror("Error", "Height cannot be zero."); return
        bmi = weight_kg / ((height_cm / 100) ** 2)
        data = {'Age': [age], 'BMI': [bmi], 'Stress Level': [stress], 'Sleep Hours': [sleep]}; df = pd.DataFrame(data)
        mood_pred_encoded, cramp_pred = app.mood_model.predict(df), app.cramp_model.predict(df)
        mood_pred = app.label_encoders['mood'].inverse_transform(mood_pred_encoded)
        cramp_risk = "High" if cramp_pred[0] == 1 else "Low"
        app.forecast_result.config(text=f"Forecast: {mood_pred[0]}, Cramp Risk: {cramp_risk}\n(BMI: {bmi:.1f})")
    except ValueError: messagebox.showerror("Input Error", "Age, Weight, Height must be numbers.")

def create_reminders_tab(app, frame):
    inner_frame = ttk.Frame(frame); inner_frame.pack(expand=True, padx=20, pady=20)
    ttk.Label(inner_frame, text="Set a New Reminder", font=("Helvetica", 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,15))
    ttk.Label(inner_frame, text="Date:").grid(row=1, column=0, sticky='w', pady=5)
    app.reminder_date = DateEntry(inner_frame, width=15, background=app.colors['accent'], foreground='white', borderwidth=2); app.reminder_date.grid(row=1, column=1, sticky='w', pady=5)
    ttk.Label(inner_frame, text="Message:").grid(row=2, column=0, sticky='w', pady=5)
    app.reminder_message = ttk.Entry(inner_frame, width=40); app.reminder_message.grid(row=2, column=1, pady=5)
    ttk.Button(inner_frame, text="⏰ Set Reminder", command=lambda: save_reminder(app)).grid(row=3, column=0, columnspan=2, pady=20)

def save_reminder(app):
    date, message = app.reminder_date.get_date().strftime('%Y-%m-%d'), app.reminder_message.get()
    if not message: messagebox.showerror("Error", "Enter reminder message."); return
    db.add_reminder(app.user_id, date, message)
    messagebox.showinfo("Success", f"Reminder set for {date}!")
    app.reminder_message.delete(0, tk.END)
    last_date_obj = app.last_period_date.get_date() if hasattr(app, 'last_period_date') and app.last_period_date.get() else None
    cycle_length_str = app.avg_cycle_length.get() if hasattr(app, 'avg_cycle_length') else '28'
    update_dashboard(app, last_date_obj, int(cycle_length_str or '28'))

def create_meditate_tab(app, frame):
    notebook = ttk.Notebook(frame); notebook.pack(pady=10, padx=10, expand=True, fill='both')
    timer_frame, guided_frame, moments_frame = ttk.Frame(notebook), ttk.Frame(notebook), ttk.Frame(notebook)
    notebook.add(timer_frame, text='⏳ Timer'); notebook.add(guided_frame, text='🎧 Guided'); notebook.add(moments_frame, text='✨ Moments')
    # Timer Section
    timer_content_frame = ttk.Frame(timer_frame); timer_content_frame.pack(expand=True)
    ttk.Label(timer_content_frame, text="Simple Meditation Timer", font=("Helvetica", 14, 'bold')).pack(pady=10)
    ttk.Label(timer_content_frame, text="Select Duration (minutes):").pack(pady=5)
    app.timer_duration = ttk.Combobox(timer_content_frame, values=[1, 3, 5, 10, 15, 20, 30], width=5); app.timer_duration.set(5); app.timer_duration.pack(pady=5)
    app.timer_label = ttk.Label(timer_content_frame, text="00:00", font=("Helvetica", 24, 'bold')); app.timer_label.pack(pady=10)
    timer_button_frame = ttk.Frame(timer_content_frame); timer_button_frame.pack(pady=10)
    app.timer_start_button = ttk.Button(timer_button_frame, text="Start", command=lambda: start_timer(app), style='Meditate.TButton'); app.timer_start_button.pack(side='left', padx=5)
    app.timer_stop_button = ttk.Button(timer_button_frame, text="Stop", command=lambda: stop_timer(app), state='disabled', style='Meditate.TButton'); app.timer_stop_button.pack(side='left', padx=5)
    # Guided Section
    guided_content_frame = ttk.Frame(guided_frame); guided_content_frame.pack(expand=True, fill='both', padx=20, pady=20)
    ttk.Label(guided_content_frame, text="Guided Meditations", font=("Helvetica", 14, 'bold')).pack(pady=10)
    guided_button_frame = ttk.Frame(guided_content_frame); guided_button_frame.pack(pady=10, fill='x')
    app.guided_text = scrolledtext.ScrolledText(guided_content_frame, wrap=tk.WORD, height=15, state='disabled', bg='white', fg=app.colors['fg'], font=('Helvetica', 11)); app.guided_text.pack(pady=10, fill='both', expand=True)
    for key, (title, _) in GUIDED_MEDITATIONS.items(): button = ttk.Button(guided_button_frame, text=title.split(" ")[0] + " " + title.split(" ")[-1], command=lambda k=key: show_guided_meditation(app, k), style='Meditate.TButton'); button.pack(side='left', padx=10, pady=5, expand=True)
    show_guided_meditation(app, None)
    # Moments Section
    moments_content_frame = ttk.Frame(moments_frame); moments_content_frame.pack(expand=True)
    ttk.Label(moments_content_frame, text="Mindfulness Moments", font=("Helvetica", 14, 'bold')).pack(pady=20)
    app.moment_label = ttk.Label(moments_content_frame, text="Click below for a quick mindfulness exercise.", wraplength=400, justify='center'); app.moment_label.pack(pady=10)
    ttk.Button(moments_content_frame, text="✨ Show a Moment", command=lambda: show_mindfulness_moment(app), style='Meditate.TButton').pack(pady=20)

def start_timer(app):
    try:
        minutes = int(app.timer_duration.get()); app.timer_remaining = minutes * 60
        app.timer_start_button.config(state='disabled'); app.timer_stop_button.config(state='normal')
        update_timer_label(app); messagebox.showinfo("Meditation Start", "Timer started.")
        app.timer_id = app.root.after(1000, lambda: timer_tick(app))
    except ValueError: messagebox.showerror("Error", "Select a valid duration.")

def stop_timer(app):
    if hasattr(app, 'timer_id') and app.timer_id: app.root.after_cancel(app.timer_id); app.timer_id = None
    app.timer_remaining = 0; update_timer_label(app)
    app.timer_start_button.config(state='normal'); app.timer_stop_button.config(state='disabled')
    messagebox.showinfo("Meditation Stop", "Timer stopped.")

def timer_tick(app):
    if app.timer_remaining > 0:
        app.timer_remaining -= 1; update_timer_label(app)
        app.timer_id = app.root.after(1000, lambda: timer_tick(app))
    else:
        stop_timer(app); messagebox.showinfo("Meditation Complete", "Well done! ✨")

def update_timer_label(app):
    mins, secs = divmod(app.timer_remaining, 60)
    app.timer_label.config(text=f"{mins:02d}:{secs:02d}")

def show_guided_meditation(app, key):
    app.guided_text.config(state='normal'); app.guided_text.delete('1.0', tk.END)
    if key and key in GUIDED_MEDITATIONS:
        title, content = GUIDED_MEDITATIONS[key]
        app.guided_text.insert(tk.END, title + "\n\n", ('title',)); app.guided_text.insert(tk.END, content)
    else: app.guided_text.insert(tk.END, "Select a guided meditation.")
    app.guided_text.tag_config('title', font=('Helvetica', 14, 'bold'), foreground=app.colors['accent'])
    app.guided_text.config(state='disabled')

def show_mindfulness_moment(app):
    app.moment_label.config(text=random.choice(MINDFULNESS_MOMENTS))

def create_symptom_checker_tab(app, frame):
    app.symptom_vars = {}
    symptoms = [("Irregular or Missed Periods", "pcos"), ("Heavy Menstrual Bleeding", "pcos"), ("Excessive Hair Growth", "pcos"), ("Acne or Oily Skin", "pcos"), ("Weight Gain / Difficulty Losing Weight", "pcos_thyroid"), ("Hair Loss or Thinning", "pcos_thyroid"), ("Fatigue or Low Energy", "thyroid"), ("Anxiety or Depression", "pcos_thyroid"), ("Sensitivity to Cold or Heat", "thyroid")]
    ttk.Label(frame, text="Check any symptoms you are experiencing:", font=("Helvetica", 12)).pack(pady=15, padx=20, anchor='w')
    symptom_frame = ttk.Frame(frame); symptom_frame.pack(fill='x', padx=20)
    for i, (symptom, category) in enumerate(symptoms):
        app.symptom_vars[symptom] = tk.BooleanVar()
        cb = ttk.Checkbutton(symptom_frame, text=symptom, variable=app.symptom_vars[symptom], style='TCheckbutton'); cb.grid(row=i, column=0, sticky='w', pady=4)
    ttk.Button(frame, text="Analyze Symptoms & Get Advice", command=lambda: analyze_symptoms(app)).pack(pady=20)
    app.advice_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=10, state='disabled', bg='white', fg=app.colors['fg'], font=('Helvetica', 10)); app.advice_text.pack(pady=10, padx=20, fill='both', expand=True)

def analyze_symptoms(app):
    selected_symptoms = [symptom for symptom, var in app.symptom_vars.items() if var.get()]
    if not selected_symptoms: messagebox.showinfo("No Symptoms", "Select symptoms first."); return
    pcos_score, thyroid_score = 0, 0
    symptom_map = dict([("Irregular or Missed Periods", "pcos"), ("Heavy Menstrual Bleeding", "pcos"), ("Excessive Hair Growth", "pcos"), ("Acne or Oily Skin", "pcos"), ("Weight Gain / Difficulty Losing Weight", "pcos_thyroid"), ("Hair Loss or Thinning", "pcos_thyroid"), ("Fatigue or Low Energy", "thyroid"), ("Anxiety or Depression", "pcos_thyroid"), ("Sensitivity to Cold or Heat", "thyroid")])
    advice = "--- Personalized Advice ---\n\n"; summary = "--- Summary ---\n"
    for symptom in selected_symptoms:
        category = symptom_map.get(symptom, ""); 
        if "pcos" in category: pcos_score += 1
        if "thyroid" in category: thyroid_score += 1
        # Add advice snippets...
        if symptom == "Weight Gain / Difficulty Losing Weight": advice += "👉 For Weight Management: Focus on a low-glycemic diet and reduce processed sugars. Regular exercise is also key.\n\n"
        if symptom == "Acne or Oily Skin": advice += "👉 For Skin Health: Consider reducing dairy and high-sugar foods. Ensure you're getting enough zinc.\n\n"
        if symptom == "Fatigue or Low Energy": advice += "👉 To Boost Energy: Check your iron levels. Incorporate iron-rich foods like spinach and lentils.\n\n"
        if symptom in ["Irregular or Missed Periods", "Heavy Menstrual Bleeding"]: advice += "👉 For Cycle Regularity: Healthy fats (avocado, nuts) and magnesium can support hormonal balance.\n\n"

    if pcos_score >= 3: summary += "Symptoms suggest potential PCOS.\n"
    if thyroid_score >= 2: summary += "Symptoms suggest potential thyroid condition.\n"
    if pcos_score < 3 and thyroid_score < 2: summary += "Monitoring symptoms is good.\n"
    summary += "\n🚨 Disclaimer: Not a medical diagnosis. Consult a professional.\n\n"
    app.advice_text.config(state='normal'); app.advice_text.delete('1.0', tk.END); app.advice_text.insert(tk.END, summary + advice); app.advice_text.config(state='disabled')

def create_graphs_tab(app, frame):
    app.fig, app.ax = plt.subplots(figsize=(7, 4), facecolor=app.colors['bg'])
    app.ax.set_facecolor(app.colors['primary'])
    canvas = FigureCanvasTkAgg(app.fig, master=frame); canvas.get_tk_widget().pack(pady=10, padx=10, fill='both', expand=True)
    toolbar = NavigationToolbar2Tk(canvas, frame); toolbar.update(); canvas.get_tk_widget().pack()
    app.graph_canvas = canvas
    ttk.Button(frame, text="📊 Show/Refresh Graph", command=lambda: plot_graphs(app)).pack(pady=10)

def plot_graphs(app):
    df = db.get_logs(app.user_id)
    if df.empty or len(df) < 2: messagebox.showerror("Error", "Not enough log data."); return
    try:
        df['date'] = pd.to_datetime(df['date']); df = df.sort_values('date') 
        app.ax.clear()
        mood_values = getattr(app, 'log_entries', {}).get('Mood', {}).get('values', [])
        if not mood_values: messagebox.showerror("Error", "Mood list not available."); return
        mood_map = {mood.split(" ")[1]: i for i, mood in enumerate(mood_values)}
        df['mood_num'] = df['mood'].map(mood_map)
        app.ax.plot(df['date'], df['mood_num'], marker='o', linestyle='-', label='Mood', color=app.colors['accent'])
        df['cramp_intensity'] = pd.to_numeric(df['cramp_intensity'])
        app.ax.plot(df['date'], df['cramp_intensity'], marker='x', linestyle='--', label='Cramp Intensity', color=app.colors['secondary'])
        app.ax.set_title('Mood & Cramp Intensity'); app.ax.set_xlabel('Date'); app.ax.set_ylabel('Level / Intensity')
        app.ax.legend()
        locator = mdates.AutoDateLocator(); formatter = mdates.ConciseDateFormatter(locator)
        app.ax.xaxis.set_major_locator(locator); app.ax.xaxis.set_major_formatter(formatter)
        app.fig.tight_layout(); app.graph_canvas.draw()
    except Exception as e: messagebox.showerror("Graph Error", f"Error: {e}")

def create_weekly_summary_tab(app, frame):
    inner_frame = ttk.Frame(frame); inner_frame.pack(expand=True, padx=20, pady=20, fill='both')
    app.summary_text = scrolledtext.ScrolledText(inner_frame, wrap=tk.WORD, height=15, bg='white', fg=app.colors['fg'], font=('Helvetica', 11)); app.summary_text.pack(pady=10, padx=10, fill='both', expand=True)
    ttk.Button(inner_frame, text="📅 Generate Weekly Summary", command=lambda: generate_summary(app)).pack(pady=10)

def generate_summary(app):
    df = db.get_logs(app.user_id)
    if df.empty: messagebox.showerror("Error", "No log data."); return
    try:
        df['date'] = pd.to_datetime(df['date']); df_last_week = df[df['date'] >= datetime.now() - timedelta(days=7)]
        if df_last_week.empty or len(df_last_week) < 2: app.summary_text.delete('1.0', tk.END); app.summary_text.insert(tk.INSERT, "Not enough data."); return
        summary = "🌸 Weekly Summary 🌸\n\n"
        summary += f"😴 Avg Sleep: {pd.to_numeric(df_last_week['sleep_hours']).mean():.2f} hrs\n"
        summary += f"🧘 Avg Stress: {pd.to_numeric(df_last_week['stress_level']).mean():.2f}/10\n"
        summary += f"💢 Avg Cramps: {pd.to_numeric(df_last_week['cramp_intensity']).mean():.2f}/10\n\n"
        summary += "😊 Mood Trends:\n" + str(df_last_week['mood'].value_counts()) + "\n\n"
        df_last_week['custom_tags'] = df_last_week['custom_tags'].fillna('')
        all_tags = [tag.strip() for tags in df_last_week['custom_tags'] for tag in tags.split(',') if tag.strip()]
        if all_tags: summary += "🏷️ Your Tags:\n" + str(pd.Series(all_tags).value_counts()) + "\n\n"
        summary += "✨ Personalized Insight ✨\n"
        insight = "" # (insight logic)
        summary += insight if insight else "You're doing a great job logging!"
        app.summary_text.delete('1.0', tk.END); app.summary_text.insert(tk.INSERT, summary)
    except Exception as e: messagebox.showerror("Summary Error", f"Error: {e}")

def create_learn_tab(app, frame):
    button_frame = ttk.Frame(frame); button_frame.pack(side='left', fill='y', padx=(20,10), pady=20)
    app.article_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state='disabled', bg='white', fg=app.colors['fg'], font=('Helvetica', 11), padx=10, pady=10); app.article_text.pack(side='right', fill='both', expand=True, padx=(10,20), pady=20)
    
    # --- UPDATED ARTICLES WITH YOGA ---
    app.articles = {
        "Cycle": ("Understanding Your Cycle 🩸", 
                  ("Your menstrual cycle has four main phases:\n\n"
                   "1. Menstrual Phase: Your period. The uterine lining sheds (3-7 days). Energy is lowest.\n\n"
                   "2. Follicular Phase: From period start until ovulation. Egg growth stimulated. Energy rises.\n\n"
                   "3. Ovulation Phase: Release of an egg (fertile window). Energy/libido peak.\n\n"
                   "4. Luteal Phase: Body prepares for pregnancy. If none, hormones drop, leading to PMS/period.")),
        "Cramps": ("Foods that Help with Cramps 🥑",
                   ("Certain foods can help ease cramps:\n\n"
                    "• Dark Chocolate: Magnesium relaxes muscles.\n\n"
                    "• Fatty Fish (Salmon): Omega-3s fight inflammation.\n\n"
                    "• Ginger & Turmeric: Natural anti-inflammatories.\n\n"
                    "• Leafy Greens (Spinach): Calcium/Magnesium ease cramping.\n\n"
                    "• Bananas: Potassium reduces bloating.")),
        "Exercise": ("Exercise & Your Hormones 🏃‍♀️",
                     ("Match exercise to your cycle phase:\n\n"
                      "• Menstrual Phase: Gentle movement (walking, yoga).\n\n"
                      "• Follicular/Ovulation Phase: Higher energy for cardio, HIIT, strength.\n\n"
                      "• Luteal Phase: Moderate intensity (strength, pilates).")),
        "PMS": ("Managing PMS Symptoms 🧘‍♀️",
                ("Tips for PMS (starts 1-2 weeks before period):\n\n"
                 "• Reduce Salt & Sugar: Helps bloating/mood.\n\n"
                 "• Increase Calcium & Magnesium: Dairy, nuts, seeds, greens.\n\n"
                 "• Stay Hydrated: Helps bloating/headaches.\n\n"
                 "• Gentle Exercise: Walking/yoga boosts mood.\n\n"
                 "• Prioritize Sleep: Aim for 7-9 hours.")),
        "PCOS": ("PCOS & Hormonal Health 🩺",
                 ("PCOS is a common hormonal disorder requiring diagnosis. Lifestyle helps management:\n\n"
                  "• Key Symptoms: Irregular periods, acne, excess hair, weight gain.\n\n"
                  "• Diet: Low-GI (whole grains, lean protein, veggies) helps manage insulin.\n\n"
                  "• Exercise: Improves insulin use, weight, mood.\n\n"
                  "Work with a doctor for diagnosis/treatment.")),
        "Doctor": ("When to See a Doctor 👩‍⚕️",
                   ("Consult a doctor if you experience:\n\n"
                    "• Sudden Cycle Changes\n• Severe Pain\n• Heavy Bleeding\n• Missed Periods (>3 consecutive)\n• Hormonal Imbalance Signs")),
         "Yoga": ("Yoga for Cycle Relief 🧘", # UPDATED YOGA CONTENT
                  ("Gentle yoga can ease discomfort, reduce stress, and balance energy. Listen to your body.\n\n"
                   "**Poses for Cramps & Relaxation:**\n\n"
                   "• Child's Pose (Balasana):\n   - Kneel, fold forward, rest forehead on floor.\n   - Benefit: Calms mind, gently stretches lower back & hips.\n\n"
                   "• Cat-Cow Pose (Marjaryasana-Bitilasana):\n   - On hands & knees. Inhale, arch back (Cow). Exhale, round spine (Cat).\n   - Benefit: Warms spine, relieves back/pelvic tension.\n\n"
                   "• Supine Spinal Twist (Supta Matsyendrasana):\n   - Lie on back, drop knees to one side, gaze opposite.\n   - Benefit: Aids digestion (bloating), releases lower back.\n\n"
                   "• Butterfly Pose (Baddha Konasana):\n   - Sit tall, soles of feet together, knees open.\n   - Benefit: Opens hips, stimulates abdominal organs, can ease cramps.\n\n"
                   "• Reclined Butterfly (Supta Baddha Konasana):\n   - Lie back in Butterfly Pose (support knees if needed).\n   - Benefit: Very restorative, gentle hip opener, promotes relaxation.\n\n"
                   "**Poses for Stress & Mood:**\n\n"
                   "• Legs-Up-The-Wall (Viparita Karani):\n   - Lie with legs resting vertically up a wall.\n   - Benefit: Calming, improves circulation, reduces fatigue.\n\n"
                   "• Corpse Pose (Savasana):\n   - Lie comfortably flat on your back, arms relaxed.\n   - Benefit: Deep relaxation, stress reduction."))
    }
    
    buttons = [
        ("Cycle", "Understanding Your Cycle"), ("Cramps", "Foods for Cramps"), ("Exercise", "Exercise & Hormones"),
        ("PMS", "Managing PMS"), ("PCOS", "PCOS & Hormonal Health"), ("Yoga", "Yoga for Cycle Relief"), 
        ("Doctor", "When to See a Doctor")
    ]
    for key, text in buttons:
        button = ttk.Button(button_frame, text=text, style='Learn.TButton', width=25, command=lambda k=key: show_article(app, k)); button.pack(pady=5, fill='x')
    show_article(app, "welcome")

def show_article(app, topic_key):
    app.article_text.config(state='normal'); app.article_text.delete('1.0', tk.END)
    title, content = ("Welcome! 📚", "Select a topic.") if topic_key == "welcome" else app.articles.get(topic_key, ("Not Found", ""))
    app.article_text.insert(tk.END, title + "\n\n", ('title',)); app.article_text.insert(tk.END, content)
    app.article_text.tag_config('title', font=('Helvetica', 14, 'bold'), foreground=app.colors['accent'])
    app.article_text.config(state='disabled')

def create_chatbot_tab(app, frame):
    app.chat_history = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state='disabled', height=18, bg='white', fg=app.colors['fg'], font=('Helvetica', 10)); app.chat_history.pack(pady=10, padx=10, fill='both', expand=True)
    input_frame = ttk.Frame(frame); input_frame.pack(pady=5, padx=10, fill='x')
    app.chat_input = ttk.Entry(input_frame, font=('Helvetica', 10)); app.chat_input.pack(side='left', fill='x', expand=True)
    app.chat_input.bind("<Return>", lambda event: get_chatbot_response(app))
    app.send_button = ttk.Button(input_frame, text="💬 Send", command=lambda: get_chatbot_response(app)); app.send_button.pack(side='right', padx=5)
    display_message(app, "🤖 Luna: Hi there! I'm Luna, your personal AI health companion. 🌸 How are you feeling today?")

def get_chatbot_response(app):
    user_input = app.chat_input.get();
    if not user_input.strip(): return
    display_message(app, "You: " + user_input)
    app.chat_input.delete(0, tk.END); app.send_button.config(state="disabled"); app.root.update_idletasks()
    response = ai_companion.get_ai_response(user_input)
    display_message(app, "🤖 Luna: " + response)
    app.send_button.config(state="normal")

def display_message(app, message):
    app.chat_history.config(state='normal'); app.chat_history.insert(tk.END, message + "\n\n"); app.chat_history.config(state='disabled'); app.chat_history.yview(tk.END)