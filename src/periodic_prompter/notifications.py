"""Notification system for Periodic Prompter."""

import tkinter as tk
from tkinter import messagebox, simpledialog
from plyer import notification
import threading
import time

# Use absolute imports for packaging compatibility
try:
    from periodic_prompter.storage import PlanStorage, LogWriter
except ImportError:
    from .storage import PlanStorage, LogWriter


class NotificationSystem:
    def __init__(self, settings=None):
        self.settings = settings
        self.storage = PlanStorage()
        self.log_writer = None
        
        # Load current plan from storage
        self.current_plan = self.storage.get_current_plan()
        
        # Initialize log writer if logging is enabled
        if settings and settings.get('create_log', True):
            log_path = settings.get('log_file_path', '~/periodic_prompter_log.txt')
            self.log_writer = LogWriter(log_path)
        
    def show_notification(self, title, message, timeout=10):
        """Show a macOS notification."""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='Periodic Prompter',
                timeout=timeout
            )
        except Exception as e:
            print(f"Failed to show notification: {e}")
            
    def show_input_dialog(self, title, prompt, previous_plan=""):
        """Show input dialog for user to enter their plan."""
        # Create a simple tkinter dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.lift()  # Bring to front
        root.attributes('-topmost', True)  # Keep on top
        
        try:
            # Create custom dialog
            dialog = tk.Toplevel(root)
            dialog.title(title)
            dialog.geometry("400x300")
            dialog.lift()
            dialog.attributes('-topmost', True)
            
            # Add previous plan if exists
            if previous_plan:
                tk.Label(dialog, text=f"Previous plan: {previous_plan}", 
                        wraplength=350, justify='left').pack(pady=10)
                tk.Label(dialog, text="Did you complete it?", 
                        font=('Arial', 10, 'bold')).pack()
                
                completion_frame = tk.Frame(dialog)
                completion_frame.pack(pady=5)
                
                completion_var = tk.StringVar(value="yes")
                tk.Radiobutton(completion_frame, text="Yes", 
                              variable=completion_var, value="yes").pack(side='left')
                tk.Radiobutton(completion_frame, text="No", 
                              variable=completion_var, value="no").pack(side='left')
                tk.Radiobutton(completion_frame, text="Partially", 
                              variable=completion_var, value="partially").pack(side='left')
            
            # Add input for new plan
            tk.Label(dialog, text=prompt, font=('Arial', 10, 'bold')).pack(pady=(10, 5))
            
            text_widget = tk.Text(dialog, height=5, width=45, wrap='word')
            text_widget.pack(pady=10, padx=10, fill='both', expand=True)
            text_widget.focus()
            
            result = {'plan': '', 'completion': 'yes'}
            
            def on_submit():
                result['plan'] = text_widget.get(1.0, tk.END).strip()
                if previous_plan:
                    result['completion'] = completion_var.get()
                dialog.destroy()
                root.quit()
            
            def on_cancel():
                result['plan'] = ''
                dialog.destroy()
                root.quit()
            
            # Buttons
            button_frame = tk.Frame(dialog)
            button_frame.pack(pady=10)
            
            tk.Button(button_frame, text="Submit", command=on_submit, 
                     bg='#007AFF', fg='white', padx=20).pack(side='left', padx=5)
            tk.Button(button_frame, text="Cancel", command=on_cancel, 
                     padx=20).pack(side='left', padx=5)
            
            # Handle window close
            dialog.protocol("WM_DELETE_WINDOW", on_cancel)
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            root.mainloop()
            
            return result
            
        except Exception as e:
            print(f"Error showing input dialog: {e}")
            return {'plan': '', 'completion': 'yes'}
        finally:
            try:
                root.destroy()
            except:
                pass
    
    def prompt_user_plan(self, previous_plan=""):
        """Show notification and prompt user for their plan."""
        # First show notification
        if previous_plan:
            message = f"Previous plan: {previous_plan}\\n\\nTime to plan your next hour!"
        else:
            message = "Time to plan your next hour!"
            
        self.show_notification("Periodic Prompter", message)
        
        # Wait a moment then show input dialog
        time.sleep(1)
        
        # Show input dialog
        title = "What are you working on?"
        prompt = "What do you plan to work on in the next hour?"
        
        result = self.show_input_dialog(title, prompt, previous_plan)
        
        if result['plan']:
            # Save to storage
            plan_entry = self.storage.save_plan(
                plan=result['plan'],
                completion_status=result.get('completion', ''),
                previous_plan=previous_plan
            )
            
            # Update current plan
            self.current_plan = result['plan']
            
            # Write to log if logging is enabled
            if self.log_writer:
                self.log_writer.write_plan_log(plan_entry)
                if self.settings and self.settings.get('create_csv_log', False):
                    self.log_writer.write_csv_log(plan_entry)
            
            # Show confirmation
            self.show_notification("Plan Recorded", f"Your plan: {result['plan'][:50]}...")
            
        return result