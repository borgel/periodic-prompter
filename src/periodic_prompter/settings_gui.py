"""Settings GUI interface for Periodic Prompter using native macOS dialogs."""

import subprocess
import json
from pathlib import Path


class SettingsWindow:
    """Native macOS dialog-based settings interface."""
    
    def __init__(self, settings, scheduler=None, notification_system=None):
        self.settings = settings
        self.scheduler = scheduler
        self.notification_system = notification_system
        
    def show(self):
        """Show the settings interface using native macOS dialogs."""
        try:
            print("Settings.show() called")
            self._show_main_settings_menu()
        except Exception as e:
            print(f"Error showing settings: {e}")
            import traceback
            traceback.print_exc()
            self._show_error_dialog(f"Error showing settings: {e}")
    
    def _show_main_settings_menu(self):
        """Show the main settings menu."""
        print("_show_main_settings_menu() called")
        current = self.settings.get_all()
        
        # Create main menu with max 3 buttons
        menu_text = f"""Current Settings:
• Interval: {current['interval_hours']} hours
• Working Hours: {current['start_time']} - {current['end_time']}
• Weekdays Only: {'Yes' if current['weekdays_only'] else 'No'}
• Logging: {'Enabled' if current['create_log'] else 'Disabled'}

What would you like to configure?"""
        
        buttons = [
            "Settings",
            "Data & Stats", 
            "Cancel"
        ]
        
        print(f"About to show choice dialog with menu_text: {menu_text}")
        choice = self._show_choice_dialog("Periodic Prompter", menu_text, buttons)
        print(f"Choice dialog returned: {choice}")
        
        if choice == "Settings":
            self._show_settings_submenu()
        elif choice == "Data & Stats":
            self._show_data_submenu()
        # Cancel does nothing
    
    def _show_settings_submenu(self):
        """Show the settings submenu."""
        buttons = [
            "Timing & Schedule",
            "Logging Settings",
            "Cancel"
        ]
        
        choice = self._show_choice_dialog("Settings", "Choose a settings category:", buttons)
        
        if choice == "Timing & Schedule":
            self._show_timing_settings()
        elif choice == "Logging Settings":
            self._show_logging_settings()
        # Cancel goes back to main menu
    
    def _show_data_submenu(self):
        """Show the data & statistics submenu."""
        buttons = [
            "Export Data",
            "View Statistics",
            "Reset to Defaults"
        ]
        
        choice = self._show_choice_dialog("Data & Statistics", "Choose an option:", buttons)
        
        if choice == "Export Data":
            self._show_export_menu()
        elif choice == "View Statistics":
            self._show_statistics()
        elif choice == "Reset to Defaults":
            self._reset_to_defaults()
        # Cancel goes back to main menu
    
    def _show_timing_settings(self):
        """Show timing and schedule settings."""
        current = self.settings.get_all()
        
        # Interval setting
        interval_text = f"Current interval: {current['interval_hours']} hours\\n\\nEnter new interval (minimum 0.1 hours = 6 minutes):"
        interval_result = self._show_input_dialog("Prompt Interval", interval_text, str(current['interval_hours']))
        
        if interval_result is None:
            return  # User cancelled
        
        try:
            interval = float(interval_result)
            if interval < 0.1:
                self._show_error_dialog("Interval must be at least 0.1 hours (6 minutes)")
                return
        except ValueError:
            self._show_error_dialog("Invalid interval. Please enter a number.")
            return
        
        # Working hours
        start_time = self._show_time_picker("Start Time", f"Current start time: {current['start_time']}")
        if start_time is None:
            return
        
        end_time = self._show_time_picker("End Time", f"Current end time: {current['end_time']}")
        if end_time is None:
            return
        
        # Weekdays only
        weekdays_choice = self._show_choice_dialog(
            "Working Days", 
            f"Current: {'Weekdays only' if current['weekdays_only'] else 'All days'}\\n\\nWhen should prompts be shown?",
            ["Weekdays only (Mon-Fri)", "All days", "Cancel"]
        )
        
        if weekdays_choice == "Cancel":
            return
        
        weekdays_only = weekdays_choice == "Weekdays only (Mon-Fri)"
        
        # Save settings
        updates = {
            'interval_hours': interval,
            'start_time': start_time,
            'end_time': end_time,
            'weekdays_only': weekdays_only
        }
        
        self.settings.update_multiple(updates)
        
        # Restart scheduler if it exists
        if self.scheduler:
            self.scheduler.restart()
        
        self._show_info_dialog("Settings Saved", "Timing settings have been updated successfully!")
    
    def _show_logging_settings(self):
        """Show logging settings."""
        current = self.settings.get_all()
        
        # Enable/disable logging
        logging_choice = self._show_choice_dialog(
            "Logging", 
            f"Current: {'Enabled' if current['create_log'] else 'Disabled'}\\n\\nDo you want to enable logging?",
            ["Enable logging", "Disable logging", "Cancel"]
        )
        
        if logging_choice == "Cancel":
            return
        
        create_log = logging_choice == "Enable logging"
        
        log_path = current['log_file_path']
        
        if create_log:
            # Get log file path
            new_path = self._show_file_save_dialog("Choose log file location", "periodic_prompter_log.txt")
            if new_path:
                log_path = new_path
        
        # Save settings
        updates = {
            'create_log': create_log,
            'log_file_path': log_path
        }
        
        self.settings.update_multiple(updates)
        
        # Update notification system log writer
        if self.notification_system:
            if create_log:
                # Use absolute imports for packaging compatibility
                try:
                    from periodic_prompter.storage import LogWriter
                except ImportError:
                    from .storage import LogWriter
                self.notification_system.log_writer = LogWriter(log_path)
            else:
                self.notification_system.log_writer = None
        
        self._show_info_dialog("Settings Saved", "Logging settings have been updated successfully!")
    
    def _show_export_menu(self):
        """Show export options."""
        if not self.notification_system or not hasattr(self.notification_system, 'storage'):
            self._show_error_dialog("Export not available - no data storage found")
            return
        
        plans = self.notification_system.storage.get_plans_history(1000)
        if not plans:
            self._show_info_dialog("No Data", "No plans found to export.")
            return
        
        export_choice = self._show_choice_dialog(
            "Export Data",
            f"Found {len(plans)} plans to export.\\n\\nChoose export format:",
            ["Export to Text", "Export to CSV", "Cancel"]
        )
        
        if export_choice == "Cancel":
            return
        
        extension = ".txt" if export_choice == "Export to Text" else ".csv"
        default_name = f"periodic_prompter_export{extension}"
        
        filename = self._show_file_save_dialog("Export plans", default_name)
        if filename:
            log_writer = self.notification_system.log_writer
            if log_writer:
                log_writer.log_file_path = Path(filename)
                format_type = 'txt' if export_choice == "Export to Text" else 'csv'
                log_writer.export_all_plans(plans, format_type)
                self._show_info_dialog("Export Complete", f"Plans exported to {filename}")
            else:
                self._show_error_dialog("Export failed - no log writer available")
    
    def _show_statistics(self):
        """Show statistics."""
        if not self.notification_system or not hasattr(self.notification_system, 'storage'):
            self._show_error_dialog("Statistics not available - no data storage found")
            return
        
        stats = self.notification_system.storage.get_stats()
        stats_text = f"""Statistics:

Total plans: {stats['total_plans']}
Completed plans: {stats['completed_plans']}
Completion rate: {stats['completion_rate']:.1f}%
Plans this week: {stats['plans_this_week']}
Plans today: {stats['plans_today']}"""
        
        self._show_info_dialog("Statistics", stats_text)
    
    def _reset_to_defaults(self):
        """Reset settings to defaults."""
        choice = self._show_choice_dialog(
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            ["Reset to Defaults", "Cancel"]
        )
        
        if choice == "Reset to Defaults":
            self.settings.reset_to_defaults()
            self._show_info_dialog("Settings Reset", "Settings have been reset to defaults.")
    
    def _show_time_picker(self, title, message):
        """Show time picker dialog using input dialog."""
        input_text = f"{message}\n\nEnter time in HH:MM format (24-hour):"
        
        while True:
            time_input = self._show_input_dialog(title, input_text, "09:00")
            if time_input is None:
                return None  # User cancelled
            
            # Validate time format
            try:
                parts = time_input.split(':')
                if len(parts) == 2:
                    hour = int(parts[0])
                    minute = int(parts[1])
                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        return f"{hour:02d}:{minute:02d}"
                
                # Invalid format, show error and try again
                self._show_error_dialog(f"Invalid time format: {time_input}. Please use HH:MM format (e.g., 09:00).")
                input_text = f"{message}\n\nEnter time in HH:MM format (24-hour):\n(Previous invalid input: {time_input})"
            except ValueError:
                self._show_error_dialog(f"Invalid time format: {time_input}. Please use HH:MM format (e.g., 09:00).")
                input_text = f"{message}\n\nEnter time in HH:MM format (24-hour):\n(Previous invalid input: {time_input})"
    
    def _show_choice_dialog(self, title, message, buttons):
        """Show a choice dialog with multiple buttons."""
        try:
            # Create buttons string for AppleScript
            buttons_str = ', '.join(f'"{btn}"' for btn in buttons)
            default_button = buttons[0]
            
            script = f'''
            set buttonChoice to button returned of (display dialog "{message}" with title "{title}" buttons {{{buttons_str}}} default button "{default_button}")
            return buttonChoice
            '''
            
            print(f"Running AppleScript: {script}")
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=True)
            
            print(f"AppleScript result: stdout='{result.stdout}', stderr='{result.stderr}'")
            return result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            print(f"AppleScript CalledProcessError: {e}, stdout='{e.stdout}', stderr='{e.stderr}'")
            return None  # User cancelled
        except Exception as e:
            print(f"Error showing choice dialog: {e}")
            return None
    
    def _show_input_dialog(self, title, message, default_value=""):
        """Show an input dialog."""
        try:
            script = f'''
            set inputText to text returned of (display dialog "{message}" with title "{title}" default answer "{default_value}")
            return inputText
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=True)
            
            return result.stdout.strip()
            
        except subprocess.CalledProcessError:
            return None  # User cancelled
        except Exception as e:
            print(f"Error showing input dialog: {e}")
            return None
    
    def _show_file_save_dialog(self, title, default_name):
        """Show file save dialog."""
        try:
            script = f'''
            set saveFile to choose file name with prompt "{title}" default name "{default_name}"
            return POSIX path of saveFile
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=True)
            
            return result.stdout.strip()
            
        except subprocess.CalledProcessError:
            return None  # User cancelled
        except Exception as e:
            print(f"Error showing file save dialog: {e}")
            return None
    
    def _show_info_dialog(self, title, message):
        """Show an info dialog."""
        try:
            script = f'''
            display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK"
            '''
            
            subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True, check=True)
            
        except Exception as e:
            print(f"Error showing info dialog: {e}")
    
    def _show_error_dialog(self, message):
        """Show an error dialog."""
        try:
            script = f'''
            display dialog "{message}" with title "Error" buttons {{"OK"}} default button "OK" with icon stop
            '''
            
            subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True, check=True)
            
        except Exception as e:
            print(f"Error showing error dialog: {e}")