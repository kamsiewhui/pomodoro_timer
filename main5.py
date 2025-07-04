import tkinter as tk
from tkinter import messagebox, simpledialog
import time
import threading
import random

class PomodoroTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rae's Room")
        self.root.geometry("600x700")  # Made taller for new features
        #self.root.resizable(False, False)
        
        # Enhanced color scheme
        self.colors = {
            'bg': '#f0f0f0',
            'title': '#2E4057',
            'accent': '#048A81', 
            'primary': '#4CAF50',
            'danger': '#f44336',
            'info': '#2196F3',
            'warning': '#FF9800'
        }
        self.root.configure(bg=self.colors['bg'])

        # Timer settings (in minutes)
        self.work_time = 25
        self.break_time = 5
        self.long_break_time = 15

        # Timer state
        self.current_time = self.work_time * 60  # Convert to seconds
        self.is_running = False
        self.is_paused = False  # NEW: Pause state
        self.is_work_session = True  # Fixed typo
        self.session_count = 0

        # NEW: Quote system enhancements
        self.quote_mode = "motivational"  # motivational or sarcastic
        self.quote_thread = None
        
        # Motivational Quotes (kept your original ones + added more)
        self.motivational_quotes = [
            "Stay focused and never give up!",
            "You're doing great! Keep going!",
            "Success is the sum of small efforts!",
            "Focus on progress, not perfection!",
            "Every minute counts towards your goals!",
            "You're stronger than you think!",
            "Great things take time and effort!",
            "Believe in yourself and keep grinding!",
            "Turn your dreams into plans, plans into actions.",
            "The expert in anything was once a beginner."
        ]
        
        # Sarcastic quotes (some longer ones to test wrapping)
        self.sarcastic_quotes = [
            "Oh look, another distraction. How surprising.",
            "Yes, checking social media is definitely more important than your goals right now.",
            "Your goals called. They're still waiting for you to show up.",
            "Breaking news: Work doesn't do itself. Shocking revelation, I know.",
            "Another break? Your focus has the attention span of a goldfish swimming in circles.",
            "I see you eyeing that phone. Don't even think about it, we both know what happens next.",
            "Wow, 2 minutes of work. You're basically unstoppable now. Nobel Prize incoming.",
            "Your productivity level: Potato. Let's aim for something more ambitious, like a slightly motivated potato.",
            "Procrastination: Because why do today what you can stress about tomorrow and panic about next week?",
            "I'm sure that notification is absolutely life-changing and cannot wait another 20 minutes."
        ]

        self.setup_ui()
        self.update_display()
        self.start_quote_rotation()  # NEW: Auto-rotating quotes

    def setup_ui(self):
        """Enhanced UI with better design"""
        # Main container for better organization
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title (enhanced styling)
        title_label = tk.Label(main_frame, text="Rae's Room",
                               font=("Arial", 28, "bold"),
                               fg=self.colors['title'],
                               bg=self.colors['bg'])
        title_label.pack(pady=(0, 10))

        # Subtitle (enhanced with session info)
        self.subtitle_label = tk.Label(main_frame, text="Grinding",
                                       font=("Arial", 16),
                                       fg=self.colors['accent'],
                                       bg=self.colors['bg'])
        self.subtitle_label.pack(pady=5)
        
        # NEW: Session counter
        self.session_label = tk.Label(main_frame, text="Sessions completed: 0",
                                     font=("Arial", 12),
                                     fg=self.colors['title'],
                                     bg=self.colors['bg'])
        self.session_label.pack(pady=5)
    
        # Timer Display (enhanced)
        self.timer_label = tk.Label(main_frame, text="25:00",
                                    font=("Courier", 48, "bold"),
                                    fg=self.colors['primary'],
                                    bg=self.colors['bg'])
        self.timer_label.pack(pady=20)

        # Button Frame
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(pady=20)

        # Start/Pause Button (MODIFIED for pause functionality)
        self.start_button = self.create_enhanced_button(
            button_frame, "Start", self.colors['primary'], self.toggle_timer
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Stop Button (enhanced styling)
        self.stop_button = self.create_enhanced_button(
            button_frame, "Stop", self.colors['danger'], self.stop_timer
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # NEW: Skip Break Button (only visible during breaks)
        self.skip_button = self.create_enhanced_button(
            button_frame, "Skip Break", self.colors['info'], self.skip_break, width=10
        )
        # Initially hidden
        self.skip_button.pack_forget()

        # NEW: Inline settings frame
        settings_frame = tk.LabelFrame(main_frame, text="Timer Settings", 
                                      font=("Arial", 12, "bold"),
                                      fg=self.colors['title'],
                                      bg=self.colors['bg'])
        settings_frame.pack(fill='x', pady=20)
        
        # Time input fields (inline instead of popup)
        time_inputs_frame = tk.Frame(settings_frame, bg=self.colors['bg'])
        time_inputs_frame.pack(pady=10)
        
        self.create_time_input(time_inputs_frame, "Work", self.work_time, 0, 
                              lambda v: setattr(self, 'work_time', v))
        self.create_time_input(time_inputs_frame, "Break", self.break_time, 1,
                              lambda v: setattr(self, 'break_time', v))
        self.create_time_input(time_inputs_frame, "Long Break", self.long_break_time, 2,
                              lambda v: setattr(self, 'long_break_time', v))

        # NEW: Quote mode toggle
        quote_control_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        quote_control_frame.pack(pady=10)
        
        quote_mode_label = tk.Label(quote_control_frame, text="Quote Mode:",
                                   font=("Arial", 12),
                                   fg=self.colors['title'],
                                   bg=self.colors['bg'])
        quote_mode_label.pack(side=tk.LEFT, padx=5)
        
        self.quote_mode_button = self.create_enhanced_button(
            quote_control_frame, "MOTIVATIONAL", self.colors['info'], 
            self.toggle_quote_mode, width=12
        )
        self.quote_mode_button.pack(side=tk.LEFT, padx=10)

        # NEW: Auto-updating quote display with better text wrapping
        quote_frame = tk.LabelFrame(main_frame, text="Current Quote", 
                                   font=("Arial", 10),
                                   fg=self.colors['title'],
                                   bg=self.colors['bg'])
        quote_frame.pack(fill='x', pady=10, padx=10)
        
        self.quote_display = tk.Label(quote_frame, text="",
                                     font=("Arial", 11, "italic"),
                                     fg=self.colors['accent'],
                                     bg=self.colors['bg'],
                                     wraplength=480,  # Adjusted for padding
                                     justify='center',
                                     anchor='center',
                                     height=3)  # Reserve space for up to 3 lines
        self.quote_display.pack(pady=15, padx=10, fill='x')

    def create_enhanced_button(self, parent, text, color, command, width=8):
        """Create buttons with enhanced styling and hover effects"""
        button = tk.Button(parent, text=text,
                          font=("Arial", 14, "bold"),
                          bg=color, fg="white",
                          width=width, height=2,
                          relief='raised', bd=2,
                          command=command)
        
        # Add hover effects
        def on_enter(e):
            button.config(relief='solid', bd=3)
        def on_leave(e):
            button.config(relief='raised', bd=2)
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button

    def create_time_input(self, parent, label, default_val, col, callback):
        """Create inline time input fields"""
        frame = tk.Frame(parent, bg=self.colors['bg'])
        frame.grid(row=0, column=col, padx=20, pady=5)
        
        tk.Label(frame, text=f"{label}\n(minutes)", 
                font=("Arial", 10),
                fg=self.colors['title'],
                bg=self.colors['bg']).pack()
        
        var = tk.StringVar(value=str(default_val))
        entry = tk.Entry(frame, textvariable=var, width=8, justify='center',
                        font=("Arial", 12))
        entry.pack(pady=5)
        
        def on_change(*args):
            try:
                val = int(var.get())
                if val > 0:
                    callback(val)
                    if not self.is_running and not self.is_paused:
                        self.reset_current_time()
                        self.update_display()
            except ValueError:
                pass
        
        var.trace('w', on_change)

    # NEW: Quote system methods
    def toggle_quote_mode(self):
        """Toggle between motivational and sarcastic quotes"""
        self.quote_mode = "sarcastic" if self.quote_mode == "motivational" else "motivational"
        self.quote_mode_button.config(text=self.quote_mode.upper())
        self.show_auto_quote()

    def show_auto_quote(self):
        """Display quote in the auto-updating display"""
        quotes = self.motivational_quotes if self.quote_mode == "motivational" else self.sarcastic_quotes
        quote = random.choice(quotes)
        self.quote_display.config(text=quote)

    def start_quote_rotation(self):
        """Start automatic quote rotation"""
        def rotate_quotes():
            while True:
                self.show_auto_quote()
                time.sleep(8)  # Change quote every 8 seconds
        
        self.quote_thread = threading.Thread(target=rotate_quotes, daemon=True)
        self.quote_thread.start()

    def reset_current_time(self):
        """Reset current time based on session type"""
        if self.is_work_session:
            self.current_time = self.work_time * 60
        else:
            if self.session_count % 4 == 0 and self.session_count > 0:
                self.current_time = self.long_break_time * 60
            else:
                self.current_time = self.break_time * 60

    def update_display(self):
        """Update timer display with enhanced styling"""
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        self.timer_label.config(text=time_text)

        # Update subtitle and colors based on session type
        if self.is_work_session:
            self.subtitle_label.config(text="Grinding", fg=self.colors['accent'])
            self.timer_label.config(fg=self.colors['primary'])
        else:
            self.subtitle_label.config(text="Break Time", fg=self.colors['primary'])
            self.timer_label.config(fg=self.colors['warning'])
        
        # Update session counter
        self.session_label.config(text=f"Sessions completed: {self.session_count}")

    # MODIFIED: Toggle timer with pause functionality and break-skip logic
    def toggle_timer(self):
        """Start, pause, or resume timer"""
        if not self.is_running and not self.is_paused:
            # Start timer
            self.start_timer()
        elif self.is_running:
            # Special case: If pausing during break, skip to work session
            if not self.is_work_session:
                self.skip_to_work_session()
            else:
                # Normal pause during work session
                self.pause_timer()
        elif self.is_paused:
            # Resume timer
            self.resume_timer()

    def start_timer(self):
        """Start timer"""
        self.is_running = True
        self.is_paused = False
        self.start_button.config(text="Pause", bg=self.colors['warning'])
        
        # Show/hide skip button based on session type
        if not self.is_work_session:
            self.skip_button.pack(side=tk.LEFT, padx=10)
        else:
            self.skip_button.pack_forget()
            
        self.countdown_thread = threading.Thread(target=self.countdown)
        self.countdown_thread.daemon = True
        self.countdown_thread.start()

    def pause_timer(self):
        """Pause timer"""
        self.is_running = False
        self.is_paused = True
        self.start_button.config(text="Resume", bg=self.colors['info'])

    def resume_timer(self):
        """Resume timer"""
        self.is_running = True
        self.is_paused = False
        self.start_button.config(text="Pause", bg=self.colors['warning'])
        self.countdown_thread = threading.Thread(target=self.countdown)
        self.countdown_thread.daemon = True
        self.countdown_thread.start()

    def stop_timer(self):
        """Stop timer and reset"""
        self.is_running = False
        self.is_paused = False
        self.start_button.config(text="Start", bg=self.colors['primary'])
        
        # Hide skip button and reset to work session
        self.skip_button.pack_forget()
        self.is_work_session = True
        
        # Reset to original time
        self.reset_current_time()
        self.update_display()
        
    # NEW: Skip break functionality
    def skip_break(self):
        """Skip current break and go directly to work session"""
        if not self.is_work_session:
            self.skip_to_work_session()
    
    def skip_to_work_session(self):
        """Transition directly to work session"""
        self.is_running = False
        self.is_paused = False
        self.is_work_session = True
        self.current_time = self.work_time * 60
        self.skip_button.pack_forget()
        self.start_button.config(text="Start", bg=self.colors['primary'])
        self.update_display()
        messagebox.showinfo("Break Skipped", "Ready to get back to work!")

    def countdown(self):
        """Countdown logic (unchanged)"""
        while self.is_running and self.current_time > 0:
            time.sleep(1)
            if self.is_running:
                self.current_time -= 1
                self.root.after(0, self.update_display)

        if self.is_running:
            self.root.after(0, self.timer_finished)

    def timer_finished(self):
        """Enhanced timer finished with auto-cycling"""
        self.is_running = False
        self.is_paused = False

        if self.is_work_session:
            self.session_count += 1
            messagebox.showinfo("Time's Up!", "Work session completed! Time for a break!")
            self.is_work_session = False

            # Determine break type
            if self.session_count % 4 == 0:
                self.current_time = self.long_break_time * 60
                messagebox.showinfo("Long Break!", f"You've completed {self.session_count} sessions! Take a {self.long_break_time} minute break!")
            else:
                self.current_time = self.break_time * 60
        else:
            messagebox.showinfo("Break Over!", "Break time is over! Get ready to grind!")
            self.is_work_session = True
            self.current_time = self.work_time * 60

        # Auto-start next phase
        self.update_display()
        self.start_timer()  # Automatically start next phase

    # Keep your original quote method for backward compatibility
    def show_quote(self):
        """Display motivational quotes (kept for compatibility)"""
        quotes = self.motivational_quotes if self.quote_mode == "motivational" else self.sarcastic_quotes
        quote = random.choice(quotes)
        messagebox.showinfo("Motivation", quote)

    # Removed the separate settings window - now inline
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = PomodoroTimer()
    app.run()