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
            # Try using native macOS notifications first
            import subprocess
            script = f'''
            display notification "{message}" with title "{title}" subtitle "Periodic Prompter"
            '''
            subprocess.run(['osascript', '-e', script], check=True)
        except Exception as e:
            try:
                # Fallback to plyer if available
                notification.notify(
                    title=title,
                    message=message,
                    app_name='Periodic Prompter',
                    timeout=timeout
                )
            except Exception as e2:
                print(f"Failed to show notification: {e}, {e2}")
            
    def show_input_dialog(self, title, prompt, previous_plan=""):
        """Show input dialog using native macOS dialog."""
        import subprocess
        
        try:
            # Build the AppleScript for the dialog
            if previous_plan:
                completion_prompt = f'set completion to button returned of (display dialog "Previous plan: {previous_plan}\\n\\nDid you complete it?" buttons {{"Yes", "No", "Partially"}} default button "Yes")'
                plan_prompt = f'set planText to text returned of (display dialog "{prompt}" default answer "" with title "{title}")'
                script = f'''
                {completion_prompt}
                {plan_prompt}
                return completion & "|" & planText
                '''
            else:
                script = f'''
                set planText to text returned of (display dialog "{prompt}" default answer "" with title "{title}")
                return "yes|" & planText
                '''
            
            # Execute the AppleScript
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                parts = result.stdout.strip().split('|', 1)
                completion = parts[0].lower() if len(parts) > 1 else 'yes'
                plan = parts[1] if len(parts) > 1 else parts[0]
                return {'plan': plan, 'completion': completion}
            else:
                return {'plan': '', 'completion': 'yes'}
                
        except subprocess.CalledProcessError:
            # User cancelled or error occurred
            return {'plan': '', 'completion': 'yes'}
        except Exception as e:
            print(f"Error showing native dialog: {e}")
            # Fallback to simple text input
            try:
                script = f'text returned of (display dialog "{prompt}" default answer "")'
                result = subprocess.run(['osascript', '-e', script], 
                                      capture_output=True, text=True, check=True)
                plan = result.stdout.strip()
                return {'plan': plan, 'completion': 'yes'}
            except:
                return {'plan': '', 'completion': 'yes'}
    
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