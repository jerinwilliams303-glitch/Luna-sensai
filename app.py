import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime

# Import our new modules
import database as db
import ui_components
import ml_models
import ai_companion

class LoginWindow:
    # This class remains unchanged from the previous version.
    # It handles the initial user login and signup.
    def __init__(self, root):
        self.root = root
        self.root.withdraw() 
        self.login_window = tk.Toplevel(root)
        self.login_window.title("Luna Sensai - Login")
        window_width, window_height = 400, 300
        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.login_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.login_window.configure(bg='#FFF0F5')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#FFF0F5')
        style.configure('Login.TButton', font=('Helvetica', 10, 'bold'), padding=10)
        style.configure('Login.TLabel', background='#FFF0F5', font=('Helvetica', 11))
        main_frame = ttk.Frame(self.login_window, style='TFrame')
        main_frame.pack(expand=True, padx=30, pady=20)
        ttk.Label(main_frame, text="Welcome to Luna Sensai", font=('Helvetica', 16, 'bold'), background='#FFF0F5').pack(pady=(0, 20))
        ttk.Label(main_frame, text="Username:", style='Login.TLabel').pack(anchor='w')
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(fill='x', pady=5)
        ttk.Label(main_frame, text="Password:", style='Login.TLabel').pack(anchor='w')
        self.password_entry = ttk.Entry(main_frame, show="*", width=30)
        self.password_entry.pack(fill='x', pady=5)
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Login", command=self.login, style='Login.TButton').pack(side='left', padx=10)
        ttk.Button(button_frame, text="Sign Up", command=self.signup, style='Login.TButton').pack(side='left', padx=10)
        self.login_window.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        user_id = db.check_user(username, password)
        if user_id:
            self.login_window.destroy()
            self.root.deiconify()
            MenstrualHealthTracker(self.root, user_id)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password to sign up.")
            return
        if db.add_user(username, password):
            messagebox.showinfo("Success", "Account created successfully! You can now log in.")
        else:
            messagebox.showerror("Error", "Username already exists. Please choose another.")


class MenstrualHealthTracker:
    def __init__(self, root, user_id):
        # Clear any previous widgets from the root window
        for widget in root.winfo_children():
            widget.destroy()

        # --- Core App Properties ---
        self.root = root
        self.user_id = user_id
        self.username = db.get_username(self.user_id)
        self.root.title(f"🌸 Luna Sensai - Logged in as {self.username}")
        self.root.geometry("950x800")
        self.colors = {'bg': '#FFF0F5', 'fg': '#333333', 'primary': '#E6E6FA', 'secondary': '#DDA0DD', 'accent': '#9370DB', 'btn_bg': '#DDA0DD', 'btn_fg': '#FFFFFF', 'btn_hover': '#C187C1'}
        self.timer_id = None # For the meditation timer

        # --- Initialize Models and UI ---
        self.setup_styles()
        # Train ML models from the ml_models module
        self.mood_model, self.cramp_model, self.label_encoders = ml_models.train_mood_cramp_models()
        
        # Build the main interface
        self.create_header()
        self.create_widgets()
        self.create_status_bar()
        
        # Initial checks
        self.check_reminders()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', background=self.colors['primary'], foreground=self.colors['fg'], padding=[10, 5], font=('Helvetica', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', self.colors['accent'])], foreground=[('selected', 'white')])
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'], font=('Helvetica', 11))
        style.configure('Header.TLabel', font=('Helvetica', 18, 'bold'))
        style.configure('Result.TLabel', foreground=self.colors['accent'], font=('Helvetica', 12, 'bold'))
        style.configure('TButton', background=self.colors['btn_bg'], foreground=self.colors['btn_fg'], font=('Helvetica', 10, 'bold'), borderwidth=0, padding=10)
        style.map('TButton', background=[('active', self.colors['btn_hover'])])
        style.configure('Learn.TButton', font=('Helvetica', 11, 'bold'), padding=[15,10])
        style.configure('Meditate.TButton', font=('Helvetica', 10), padding=8) # Style for meditation buttons
        style.configure('TEntry', fieldbackground='white', foreground=self.colors['fg'])
        style.configure('TScale', background=self.colors['bg'])
        style.configure('TCheckbutton', background=self.colors['bg'], font=('Helvetica', 10))

    def create_header(self):
        header_frame = ttk.Frame(self.root, style='TFrame')
        header_frame.pack(pady=20, fill='x', padx=20)
        try:
            img = Image.open("icon.png").resize((64, 64), Image.LANCZOS)
            self.app_icon = ImageTk.PhotoImage(img)
            icon_label = ttk.Label(header_frame, image=self.app_icon, style='TLabel')
            icon_label.pack(side='left', padx=10)
        except FileNotFoundError:
            pass
        ttk.Label(header_frame, text="Luna Sensai", style='Header.TLabel').pack(side='left')
        exit_button = ttk.Button(header_frame, text="Exit", command=self.root.destroy, style='TButton')
        exit_button.pack(side='right', padx=10)

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, expand=True, fill='both')
        
        # Use a dictionary to define all tabs and their creation functions from ui_components
        tabs = {
            '🏠 Dashboard': ui_components.create_dashboard_tab,
            '🩸 Period Prediction': ui_components.create_period_prediction_tab,
            '📝 Daily Logging': ui_components.create_daily_logging_tab,
            '🔮 Forecasting': ui_components.create_forecasting_tab,
            '⏰ Reminders': ui_components.create_reminders_tab,
            '🧘 Meditate': ui_components.create_meditate_tab, # NEW TAB
            '🩺 Hormonal Health': ui_components.create_symptom_checker_tab,
            '📊 Graphs': ui_components.create_graphs_tab,
            '📅 Weekly Summary': ui_components.create_weekly_summary_tab,
            '📚 Learn': ui_components.create_learn_tab,
            '🤖 AI Companion Luna': ui_components.create_chatbot_tab
        }

        for i, (text, creation_func) in enumerate(tabs.items()):
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=text)
            creation_func(self, frame) # Pass the main app instance 'self' to each function
            if 'Daily Logging' in text:
                self.logging_tab_index = i

    def create_status_bar(self):
        status_frame = ttk.Frame(self.root, style='TFrame', relief='sunken')
        status_frame.pack(side='bottom', fill='x')
        ttk.Label(status_frame, text=f"Logged in as: {self.username}", style='TLabel', padding=(5,2)).pack(side='left')
        ttk.Label(status_frame, text=f"Today: {datetime.now().strftime('%Y-%m-%d')}", style='TLabel', padding=(5,2)).pack(side='right')

    def check_reminders(self):
        today_str = datetime.now().strftime('%Y-%m-%d')
        reminders = db.get_reminders_for_date(self.user_id, today_str)
        if reminders:
            reminder_text = "\n".join(f"• {r}" for r in reminders)
            messagebox.showinfo("Today's Reminders ✨", f"You have the following reminders for today:\n\n{reminder_text}")

if __name__ == "__main__":
    db.init_db()  # Initialize the database on startup
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()