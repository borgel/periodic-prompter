"""Main application entry point for Periodic Prompter."""

import sys
import os

# Fix for Carbon framework issues on modern macOS
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'


def main():
    """Main entry point."""
    if sys.platform != 'darwin':
        print("This application is designed for macOS only.")
        sys.exit(1)
    
    # Use rumps-based app instead of pystray
    try:
        from periodic_prompter.main_rumps import main as rumps_main
        rumps_main()
    except ImportError:
        from .main_rumps import main as rumps_main
        rumps_main()


if __name__ == "__main__":
    main()