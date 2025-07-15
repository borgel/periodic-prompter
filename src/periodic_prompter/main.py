"""Main application entry point for Periodic Prompter."""

import sys
import threading
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from .notifications import NotificationSystem
from .settings import Settings


class PeriodicPrompter:
    def __init__(self):
        self.settings = Settings()
        self.notification_system = NotificationSystem(self.settings)
        self.tray_icon = None
        
    def create_image(self):
        """Create a simple icon for the menu bar."""
        # Create a simple clock-like icon
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Draw a circle
        draw.ellipse([8, 8, width-8, height-8], fill='black', outline='black')
        
        # Draw clock hands
        center_x, center_y = width // 2, height // 2
        draw.line([center_x, center_y, center_x, center_y - 15], fill='white', width=2)  # Hour hand
        draw.line([center_x, center_y, center_x + 10, center_y - 5], fill='white', width=1)  # Minute hand
        
        return image
    
    def show_current_plan(self, icon, item):
        """Show the current plan in a simple way."""
        current = self.notification_system.current_plan or "No plan set yet"
        self.notification_system.show_notification("Current Plan", current)
        
    def prompt_now(self, icon, item):
        """Manually trigger a planning prompt."""
        def run_prompt():
            previous = self.notification_system.current_plan
            result = self.notification_system.prompt_user_plan(previous)
        
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=run_prompt, daemon=True).start()
        
    def open_settings(self, icon, item):
        """Open settings interface."""
        print("Opening settings...")
        # TODO: Implement settings GUI
        
    def quit_application(self, icon, item):
        """Quit the application."""
        print("Quitting Periodic Prompter...")
        icon.stop()
        
    def setup_tray_icon(self):
        """Set up the system tray icon with menu."""
        image = self.create_image()
        
        menu = pystray.Menu(
            item('Current Plan', self.show_current_plan),
            item('Prompt Now', self.prompt_now),
            item('Settings', self.open_settings),
            item('Quit', self.quit_application)
        )
        
        self.tray_icon = pystray.Icon("periodic_prompter", image, "Periodic Prompter", menu)
        
    def run(self):
        """Start the application."""
        print("Starting Periodic Prompter...")
        self.setup_tray_icon()
        
        # Start the tray icon in the main thread
        self.tray_icon.run()


def main():
    """Main entry point."""
    if sys.platform != 'darwin':
        print("This application is designed for macOS only.")
        sys.exit(1)
        
    app = PeriodicPrompter()
    app.run()


if __name__ == "__main__":
    main()