"""Main application using rumps for macOS menu bar integration."""

import sys
import threading
import os
import rumps

# Use absolute imports for packaging compatibility
try:
    from periodic_prompter.notifications import NotificationSystem
    from periodic_prompter.settings import Settings
    from periodic_prompter.scheduler import PromptScheduler
    from periodic_prompter.settings_gui import SettingsWindow
except ImportError:
    # Fallback to relative imports for development
    from .notifications import NotificationSystem
    from .settings import Settings
    from .scheduler import PromptScheduler
    from .settings_gui import SettingsWindow


class PeriodicPrompterApp(rumps.App):
    def __init__(self):
        super(PeriodicPrompterApp, self).__init__("⏰", title="⏰")
        
        # Initialize components
        self.settings = Settings()
        self.notification_system = NotificationSystem(self.settings)
        self.scheduler = PromptScheduler(self.settings, self.notification_system)
        self.settings_window = None
        
        # Set up menu
        self.menu = [
            "Current Plan",
            "Prompt Now",
            None,  # Separator
            "Schedule Info", 
            "Toggle Scheduler",
            None,  # Separator
            "Settings",
        ]
        
        # Start scheduler
        self.scheduler.start()
        
    @rumps.clicked("Current Plan")
    def show_current_plan(self, _):
        """Show the current plan."""
        current = self.notification_system.current_plan or "No plan set yet"
        self.notification_system.show_notification("Current Plan", current)
        
    @rumps.clicked("Prompt Now")
    def prompt_now(self, _):
        """Manually trigger a planning prompt."""
        def run_prompt():
            previous = self.notification_system.current_plan
            result = self.notification_system.prompt_user_plan(previous)
        
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=run_prompt, daemon=True).start()
        
    @rumps.clicked("Settings")
    def open_settings(self, _):
        """Open settings interface."""
        def show_settings():
            self.settings_window = SettingsWindow(
                self.settings, 
                self.scheduler, 
                self.notification_system
            )
            self.settings_window.show()
        
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=show_settings, daemon=True).start()
        
    @rumps.clicked("Schedule Info")
    def show_schedule_info(self, _):
        """Show information about the current schedule."""
        info = self.scheduler.get_schedule_info()
        status = "Running" if info['running'] else "Stopped"
        message = f"Scheduler: {status}\\nInterval: {info['interval_hours']}h\\nNext: {info['next_prompt']}"
        self.notification_system.show_notification("Schedule Status", message)
    
    @rumps.clicked("Toggle Scheduler")
    def toggle_scheduler(self, _):
        """Toggle the scheduler on/off."""
        if self.scheduler.running:
            self.scheduler.stop()
            self.notification_system.show_notification("Scheduler", "Automatic prompts stopped")
        else:
            self.scheduler.start()
            self.notification_system.show_notification("Scheduler", "Automatic prompts started")
    
    def clean_up_before_quit(self):
        """Clean up resources before quitting."""
        print("Cleaning up before quit...")
        self.scheduler.stop()


def main():
    """Main entry point."""
    if sys.platform != 'darwin':
        print("This application is designed for macOS only.")
        sys.exit(1)
        
    app = PeriodicPrompterApp()
    app.run()


if __name__ == "__main__":
    main()